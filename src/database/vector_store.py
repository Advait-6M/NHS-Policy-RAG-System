"""Qdrant vector store implementation for NEPPA with hybrid search support."""

import logging
import os
from typing import Any, Dict, List, Optional, Union

from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import (
    CollectionStatus,
    Distance,
    FieldCondition,
    Filter,
    Fusion,
    FusionQuery,
    Modifier,
    NearestQuery,
    PayloadSchemaType,
    PointStruct,
    Prefetch,
    Query,
    RrfQuery,
    SparseVector,
    SparseVectorParams,
    VectorParams,
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QdrantVectorStore:
    """
    Qdrant vector store with hybrid search support (dense + sparse vectors).

    Supports:
    - Dense vectors: OpenAI text-embedding-3-small (1536 dimensions)
    - Sparse vectors: FastEmbed BM25 sparse embeddings for keyword search
    - Payload indexes: source_type, priority_score, clinical_area for filtering
    """

    COLLECTION_NAME = "nhs_expert_policy"
    DENSE_VECTOR_SIZE = 1536  # OpenAI text-embedding-3-small dimension
    DENSE_VECTOR_NAME = "dense"  # Name for dense vector in hybrid search
    SPARSE_VECTOR_NAME = "sparse"  # Name for sparse vector in hybrid search

    def __init__(
        self,
        url: Optional[str] = None,
        port: int = 6333,
        grpc_port: int = 6334,
        prefer_grpc: bool = False,
    ) -> None:
        """
        Initialize Qdrant client.

        Args:
            url: Qdrant server URL (default: localhost)
            port: HTTP API port (default: 6333)
            grpc_port: gRPC API port (default: 6334)
            prefer_grpc: Whether to prefer gRPC over HTTP (default: False)
        """
        self.url = url or os.getenv("QDRANT_URL", "localhost")
        self.port = port
        self.grpc_port = grpc_port
        self.prefer_grpc = prefer_grpc

        # Initialize Qdrant client with Windows-optimized settings
        # Bypass SSL cert scanning on localhost to prevent HTTPX hang
        self.client = QdrantClient(
            url=self.url,
            port=self.port,
            grpc_port=self.grpc_port,
            prefer_grpc=False,  # Use HTTP for localhost
            https=False,  # No SSL for localhost
            timeout=10,  # Strict timeout to prevent hangs
        )
        logger.info(f"Connected to Qdrant at {self.url}:{self.port}")

    def create_collection(self, recreate: bool = False) -> None:
        """
        Create the NHS Expert Policy collection with hybrid search schema.

        Args:
            recreate: If True, delete existing collection before creating (default: False)
        """
        # Check if collection exists
        collections = self.client.get_collections().collections
        collection_exists = any(
            coll.name == self.COLLECTION_NAME for coll in collections
        )

        if collection_exists:
            if recreate:
                logger.info(f"Deleting existing collection: {self.COLLECTION_NAME}")
                self.client.delete_collection(self.COLLECTION_NAME)
            else:
                logger.info(
                    f"Collection {self.COLLECTION_NAME} already exists. Skipping creation."
                )
                return

        # Define vector configuration for hybrid search
        # Dense vector: OpenAI embeddings (named vector for hybrid search)
        # Sparse vector: FastEmbed BM25 with IDF modifier
        vectors_config = {
            self.DENSE_VECTOR_NAME: models.VectorParams(
                size=self.DENSE_VECTOR_SIZE,
                distance=Distance.COSINE,
            )
        }

        # Configure sparse vectors for BM25 keyword search
        # Qdrant uses BM25 by default for sparse vectors, we just need to set modifier=IDF
        sparse_vectors_config = {
            self.SPARSE_VECTOR_NAME: models.SparseVectorParams(
                modifier=Modifier.IDF,
            )
        }

        # Create collection with both dense and sparse vectors
        self.client.create_collection(
            collection_name=self.COLLECTION_NAME,
            vectors_config=vectors_config,
            sparse_vectors_config=sparse_vectors_config,
        )

        logger.info(f"Created collection: {self.COLLECTION_NAME}")

        # Create payload indexes for efficient filtering
        self._create_payload_indexes()

    def _create_payload_indexes(self) -> None:
        """Create payload indexes for filtering on metadata fields."""
        try:
            # Index for source_type (keyword filtering)
            self.client.create_payload_index(
                collection_name=self.COLLECTION_NAME,
                field_name="source_type",
                field_schema=PayloadSchemaType.KEYWORD,
            )
            logger.info("Created payload index: source_type")

            # Index for priority_score (numeric filtering/boosting)
            self.client.create_payload_index(
                collection_name=self.COLLECTION_NAME,
                field_name="priority_score",
                field_schema=PayloadSchemaType.FLOAT,
            )
            logger.info("Created payload index: priority_score")

            # Index for clinical_area (keyword filtering)
            self.client.create_payload_index(
                collection_name=self.COLLECTION_NAME,
                field_name="clinical_area",
                field_schema=PayloadSchemaType.KEYWORD,
            )
            logger.info("Created payload index: clinical_area")

            # Index for organization (keyword filtering)
            self.client.create_payload_index(
                collection_name=self.COLLECTION_NAME,
                field_name="organization",
                field_schema=PayloadSchemaType.KEYWORD,
            )
            logger.info("Created payload index: organization")

        except Exception as e:
            logger.warning(f"Error creating payload indexes (may already exist): {e}")

    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the collection.

        Returns:
            Dictionary with collection information
        """
        info = self.client.get_collection(self.COLLECTION_NAME)
        vector_size = (
            info.config.params.vectors.size
            if hasattr(info.config.params.vectors, "size")
            else "Unknown"
        )
        return {
            "name": self.COLLECTION_NAME,
            "vector_size": vector_size,
            "vectors_count": info.points_count,
            "indexed_vectors_count": info.indexed_vectors_count,
            "status": str(info.status),
        }

    def upsert_points(
        self,
        points: List[PointStruct],
        wait: bool = True,
    ) -> None:
        """
        Upsert points (chunks) into the collection.

        Args:
            points: List of PointStruct objects to upsert
            wait: Whether to wait for indexing to complete (default: True)
        """
        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=points,
            wait=wait,
        )
        logger.info(f"Upserted {len(points)} points to {self.COLLECTION_NAME}")

    def search(
        self,
        query_vector: List[float],
        query_sparse_vector: Optional[SparseVector] = None,
        limit: int = 10,
        score_threshold: Optional[float] = None,
        filter_conditions: Optional[Filter] = None,
        use_reranking: bool = True,
        query_text: str = "",
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search (dense + sparse vectors) with Reciprocal Rank Fusion (RRF).

        Args:
            query_vector: Dense query vector (OpenAI embedding)
            query_sparse_vector: Optional sparse query vector (BM25)
            limit: Number of results to return (default: 10)
            score_threshold: Minimum similarity score (default: None)
            filter_conditions: Optional filter conditions for payload
            use_reranking: Whether to apply custom reranking (default: True)

        Returns:
            List of search results with scores and payloads
        """
        if query_sparse_vector:
            # Hybrid search: combine dense and sparse vectors using RRF (Reciprocal Rank Fusion)
            # Use query_points with prefetch parameter - pass vectors directly to Prefetch
            # Prefetch.query accepts VectorInput (List[float] or SparseVector) directly
            query_result = self.client.query_points(
                collection_name=self.COLLECTION_NAME,
                prefetch=[
                    Prefetch(
                        query=query_vector,  # Pass vector directly, not wrapped in NearestQuery
                        using=self.DENSE_VECTOR_NAME,
                        limit=limit * 2 if use_reranking else limit,
                    ),
                    Prefetch(
                        query=query_sparse_vector,  # Pass sparse vector directly
                        using=self.SPARSE_VECTOR_NAME,
                        limit=limit * 2 if use_reranking else limit,
                    ),
                ],
                query=FusionQuery(fusion=Fusion.RRF),
                query_filter=filter_conditions,
                limit=limit * 2 if use_reranking else limit,
                score_threshold=score_threshold,
                with_payload=True,
                with_vectors=False,
            )
        else:
            # Fallback to dense-only search if sparse vector not provided
            query_result = self.client.query_points(
                collection_name=self.COLLECTION_NAME,
                query=query_vector,
                query_filter=filter_conditions,
                limit=limit * 2 if use_reranking else limit,
                score_threshold=score_threshold,
                with_payload=True,
                with_vectors=False,
            )

        # Format results
        results = []
        for point in query_result.points:
            results.append(
                {
                    "id": point.id,
                    "score": point.score,
                    "payload": point.payload,
                }
            )

        # Apply custom reranking if enabled
        if use_reranking:
            results = self.rerank_results(results, limit=limit, query_text=query_text)

        return results

    def rerank_results(
        self, results: List[Dict[str, Any]], limit: int = 10, query_text: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Rerank search results using similarity, recency, and semantic term matching.

        Final Score Formula (OPTIMIZED FOR SPRINT 8 - Version 5 - UNBIASED):
        - 50% Similarity Score (from hybrid search: dense + sparse vectors)
        - 40% Term Match Score (dynamic query-document term alignment)
        - 10% Recency Score (based on document age: 2024=1.0, linear decay)

        Rationale: Fully generalized reranking without document type bias.
        All documents (Local, National, Governance) are treated equally.
        Term matching is dynamic - extracts terms from ANY query without hardcoding.

        Args:
            results: List of search results with scores and payloads
            limit: Number of results to return after reranking

        Returns:
            Reranked list of results
        """
        from datetime import datetime
        import re

        current_year = datetime.now().year
        
        # Extract meaningful terms from query (2+ words, excluding common stop words)
        query_terms = []
        if query_text:
            query_lower = query_text.lower()
            # Simple stop word list (medical domain)
            stop_words = {"the", "a", "an", "and", "or", "for", "in", "on", "with", "to", "of", "is", "are", "what", "when", "where", "how", "should", "can"}
            # Extract words of length 3+
            words = re.findall(r'\b[a-z]{3,}\b', query_lower)
            query_terms = [w for w in words if w not in stop_words]
        
        reranked = []
        for result in results:
            payload = result.get("payload", {})
            similarity_score = result.get("score", 0.0)
            
            # Calculate recency score based on sortable_date
            recency_score = 0.5  # Default for unknown dates
            sortable_date = payload.get("sortable_date")
            if sortable_date:
                try:
                    # Parse YYYYMMDD format
                    year = int(str(sortable_date)[:4])
                    # Linear decay: 2024 = 1.0, 2022 = 0.6, so slope = (1.0 - 0.6) / (2024 - 2022) = 0.2
                    # Formula: 1.0 - 0.2 * (current_year - year)
                    years_old = current_year - year
                    recency_score = max(0.0, min(1.0, 1.0 - 0.2 * years_old))
                except (ValueError, TypeError):
                    pass
            
            # Calculate term matching score (dynamic, no hardcoded keywords)
            term_match_score = 0.0
            if query_terms:
                # Check filename and clinical_area for query term matches
                file_name = payload.get("file_name", "").lower()
                clinical_area = payload.get("clinical_area", "").lower()
                combined_text = f"{file_name} {clinical_area}"
                
                # Count how many query terms appear in document metadata
                matches = sum(1 for term in query_terms if term in combined_text)
                # Normalize: 0 matches = 0.0, 3+ matches = 1.0
                term_match_score = min(1.0, matches / 3.0)
            
            # Weighted combination: 50% similarity, 40% term match, 10% recency (V5 - UNBIASED)
            final_score = (
                0.50 * similarity_score +
                0.40 * term_match_score +
                0.10 * recency_score
            )
            
            reranked.append({
                "id": result["id"],
                "score": final_score,
                "original_score": similarity_score,
                "recency_score": recency_score,
                "term_match_score": term_match_score,
                "payload": payload,
            })
        
        # Sort by final score (descending) and limit results
        reranked.sort(key=lambda x: x["score"], reverse=True)
        return reranked[:limit]

    def delete_collection(self) -> None:
        """Delete the collection (use with caution!)."""
        self.client.delete_collection(self.COLLECTION_NAME)
        logger.warning(f"Deleted collection: {self.COLLECTION_NAME}")

    def collection_exists(self) -> bool:
        """Check if the collection exists."""
        collections = self.client.get_collections().collections
        return any(coll.name == self.COLLECTION_NAME for coll in collections)

    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get collection statistics.

        Returns:
            Dictionary with collection statistics
        """
        if not self.collection_exists():
            return {"exists": False}

        info = self.client.get_collection(self.COLLECTION_NAME)
        return {
            "exists": True,
            "points_count": info.points_count,
            "indexed_vectors_count": info.indexed_vectors_count,
            "status": str(info.status),
        }


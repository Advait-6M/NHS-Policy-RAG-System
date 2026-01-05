"""RAG Engine for expert reasoning and query processing."""

import json
import logging
import os
from typing import Any, Dict, List, Optional

import openai
from dotenv import load_dotenv
from fastembed import SparseTextEmbedding
from qdrant_client.http.models import SparseVector

from src.database.vector_store import QdrantVectorStore
from src.engine.context_formatter import (
    extract_source_metadata,
    format_context,
    format_bibliography,
)
from src.engine.prompts import QUERY_EXPANSION_PROMPT, SYSTEM_PROMPT

# Load environment variables
load_dotenv()

# Set up logging - minimal output for evaluation
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class RAGEngine:
    """
    RAG Engine for expert reasoning with query expansion, hybrid retrieval, and expert response generation.
    
    Features:
    - Query expansion using OpenAI GPT-3.5-turbo
    - Hybrid retrieval (dense + sparse vectors)
    - Context synthesis with source metadata
    - Expert system prompt with clinical guardrails
    - Response generation with citations
    """

    def __init__(
        self,
        vector_store: Optional[QdrantVectorStore] = None,
        openai_api_key: Optional[str] = None,
    ) -> None:
        """
        Initialize RAG Engine.

        Args:
            vector_store: Optional QdrantVectorStore instance (creates new if None)
            openai_api_key: Optional OpenAI API key (uses env var if None)
        """
        # Initialize vector store
        self.vector_store = vector_store or QdrantVectorStore()
        
        # Initialize OpenAI client for embeddings, query expansion, and response generation
        openai_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        # Use new OpenAI API (1.0.0+) if available, otherwise fall back to old API
        try:
            from openai import OpenAI
            self.openai_client = OpenAI(api_key=openai_key)
            self.use_new_api = True
        except (ImportError, AttributeError):
            # Fall back to old API (0.28.1)
            openai.api_key = openai_key
            self.openai_client = None
            self.use_new_api = False
        
        # Initialize sparse embedding model (for query sparse vectors)
        self.sparse_model = SparseTextEmbedding(model_name="Qdrant/bm25")
        
        logger.info("RAG Engine initialized")

    def expand_query(self, query: str) -> List[str]:
        """
        Expand user query into 3 clinical search terms using OpenAI GPT-3.5-turbo.

        Args:
            query: User query string

        Returns:
            List of 3 expanded search terms
        """
        try:
            logger.info(f"Expanding query: '{query}'")
            
            # Call OpenAI API for query expansion
            prompt = QUERY_EXPANSION_PROMPT.format(query=query)
            messages = [
                {"role": "system", "content": "You are a clinical policy search assistant. Generate exactly 3 clinical search terms as a JSON array."},
                {"role": "user", "content": prompt}
            ]
            
            if self.use_new_api:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.3,
                    max_tokens=200,
                )
                response_text = response.choices[0].message.content.strip()
            else:
                # Old API (0.28.1)
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.3,
                    max_tokens=200,
                )
                response_text = response.choices[0].message.content.strip()
            
            # Parse JSON array (remove markdown code blocks if present)
            if response_text.startswith("```"):
                # Remove markdown code blocks
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1]) if len(lines) > 2 else response_text
            
            # Parse JSON
            search_terms = json.loads(response_text)
            
            # Validate: should be list of 3 strings
            if not isinstance(search_terms, list) or len(search_terms) != 3:
                logger.warning(f"Invalid expansion format, using original query")
                return [query]
            
            # Ensure all are strings
            search_terms = [str(term) for term in search_terms]
            
            logger.info(f"Expanded to {len(search_terms)} search terms: {search_terms}")
            return search_terms
            
        except Exception as e:
            logger.warning(f"Query expansion failed: {e}. Using original query.")
            return [query]

    def _generate_dense_embedding(self, text: str) -> List[float]:
        """
        Generate dense embedding for query text.

        Args:
            text: Query text

        Returns:
            Dense embedding vector
        """
        try:
            if self.use_new_api:
                response = self.openai_client.embeddings.create(
                    model="text-embedding-3-small",
                    input=[text]
                )
                return response.data[0].embedding
            else:
                # Old API (0.28.1)
                response = openai.Embedding.create(
                    model="text-embedding-3-small",
                    input=[text]
                )
                return response["data"][0]["embedding"]
        except Exception as e:
            logger.error(f"Error generating dense embedding: {e}")
            raise

    def _generate_sparse_embedding(self, text: str) -> SparseVector:
        """
        Generate sparse embedding for query text.

        Args:
            text: Query text

        Returns:
            SparseVector object
        """
        try:
            embeddings = list(self.sparse_model.embed([text]))
            embedding = embeddings[0]
            sparse_obj = embedding.as_object()
            return SparseVector(
                indices=sparse_obj["indices"],
                values=sparse_obj["values"],
            )
        except Exception as e:
            logger.error(f"Error generating sparse embedding: {e}")
            raise

    def retrieve(
        self, 
        query: str, 
        limit: int = 10,
        use_expansion: bool = True,
        expanded_terms: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks using hybrid search with query expansion.

        Args:
            query: User query string
            limit: Maximum number of chunks to return (default: 10)
            use_expansion: Whether to expand query (default: True)
            expanded_terms: Pre-expanded search terms (if provided, skips expansion)

        Returns:
            List of retrieved chunks with scores and payloads
        """
        # Use provided expanded terms, or expand query if enabled
        if expanded_terms:
            search_terms = expanded_terms
        elif use_expansion:
            search_terms = self.expand_query(query)
        else:
            search_terms = [query]
        
        # Collect results from all expanded terms
        all_results = []
        seen_chunk_ids = set()
        
        for term in search_terms:
            try:
                # Generate embeddings
                dense_vector = self._generate_dense_embedding(term)
                sparse_vector = self._generate_sparse_embedding(term)
                
                # Execute hybrid search
                results = self.vector_store.search(
                    query_vector=dense_vector,
                    query_sparse_vector=sparse_vector,
                    limit=limit * 2,  # Get more results for deduplication
                    use_reranking=True,
                )
                
                # Deduplicate by chunk_id
                for result in results:
                    chunk_id = result.get("payload", {}).get("chunk_id")
                    if chunk_id and chunk_id not in seen_chunk_ids:
                        seen_chunk_ids.add(chunk_id)
                        all_results.append(result)
                
            except Exception as e:
                logger.error(f"Error retrieving for term '{term}': {e}")
                continue
        
        # Sort by final score (from reranking)
        all_results.sort(key=lambda x: x.get("score", 0.0), reverse=True)
        
        # Return top N results
        final_results = all_results[:limit]
        logger.info(f"Retrieved {len(final_results)} unique chunks from {len(search_terms)} search terms")
        
        return final_results

    def generate_response(
        self,
        query: str,
        context: str,
        chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate expert response using formatted context and system prompt.

        Args:
            query: User query string
            context: Formatted context string with source metadata
            chunks: List of retrieved chunks (for source metadata)

        Returns:
            Dictionary with response text and metadata
        """
        try:
            # Build messages
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"User Query: {query}\n\nContext from Policy Documents:\n\n{context}"
                }
            ]
            
            # Call OpenAI API
            logger.info("Generating response with GPT-3.5-turbo...")
            try:
                if self.use_new_api:
                    response = self.openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=messages,
                        temperature=0.3,
                        max_tokens=1500,  # Balanced for comprehensive responses
                    )
                    response_text = response.choices[0].message.content.strip()
                else:
                    # Old API (0.28.1)
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=messages,
                        temperature=0.3,
                        max_tokens=1500,  # Balanced for comprehensive responses
                    )
                    response_text = response.choices[0].message.content.strip()
            except Exception as e:
                # Fallback: try gpt-4o-mini if available
                logger.warning(f"gpt-3.5-turbo failed, trying gpt-4o-mini: {e}")
                if self.use_new_api:
                    response = self.openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages,
                        temperature=0.3,
                        max_tokens=1500,  # Balanced for comprehensive responses
                    )
                    response_text = response.choices[0].message.content.strip()
                else:
                    # Old API (0.28.1)
                    response = openai.ChatCompletion.create(
                        model="gpt-4o-mini",
                        messages=messages,
                        temperature=0.3,
                        max_tokens=1500,  # Balanced for comprehensive responses
                    )
                    response_text = response.choices[0].message.content.strip()
            
            # Extract source metadata for citations
            sources = extract_source_metadata(chunks)
            
            # Format bibliography if not already included in response
            if "Bibliography" not in response_text and "bibliography" not in response_text.lower():
                bibliography = format_bibliography(sources)
                if bibliography:
                    response_text += "\n\n" + bibliography
            
            # Note: Safety disclaimer is handled by the UI, not added to response text
            
            logger.info("Response generated successfully")
            
            return {
                "response": response_text,
                "sources": sources,
                "num_chunks": len(chunks),
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise

    def query(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Execute complete RAG pipeline: expansion → retrieval → formatting → response.

        Args:
            query: User query string
            limit: Maximum number of chunks to retrieve (default: 10)

        Returns:
            Dictionary with:
            - response: Generated response text
            - sources: List of source metadata
            - chunks: Retrieved chunks (for debugging)
            - expanded_terms: Expanded search terms (for debugging)
        """
        logger.info(f"Processing query: '{query}'")
        
        # Step 1: Expand query
        expanded_terms = self.expand_query(query)
        
        # Step 2: Retrieve chunks using pre-expanded terms (avoids double expansion)
        chunks = self.retrieve(query, limit=limit, expanded_terms=expanded_terms)
        
        if not chunks:
            return {
                "response": "Based on the current local and national policy database, I cannot find specific guidance for this query. I recommend consulting with your GP or healthcare provider for personalized advice.",
                "sources": [],
                "chunks": [],
                "expanded_terms": expanded_terms,
            }
        
        # Step 3: Format context
        context = format_context(chunks)
        
        # Step 4: Generate response
        result = self.generate_response(query, context, chunks)
        
        # Add debugging info
        result["chunks"] = chunks
        result["expanded_terms"] = expanded_terms
        
        logger.info("Query processing complete")
        return result


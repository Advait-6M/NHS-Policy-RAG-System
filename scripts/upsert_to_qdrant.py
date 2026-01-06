"""Script to upsert processed chunks to Qdrant vector database."""

import hashlib
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
import openai
from fastembed import SparseTextEmbedding
from qdrant_client.http.models import PointStruct, SparseVector

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.vector_store import QdrantVectorStore

# SPARSE_VECTOR_NAME constant for consistency
SPARSE_VECTOR_NAME = "sparse"

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def load_chunk_files(data_dir: Path) -> List[Dict[str, Any]]:
    """
    Load all chunk JSON files from the processed data directory.

    Args:
        data_dir: Path to the data/processed directory

    Returns:
        List of all chunks from all files
    """
    chunk_files = list(data_dir.glob("*_chunks.json"))
    logger.info(f"Found {len(chunk_files)} chunk files")

    all_chunks = []
    for chunk_file in chunk_files:
        try:
            with open(chunk_file, "r", encoding="utf-8") as f:
                chunks = json.load(f)
                if isinstance(chunks, list):
                    all_chunks.extend(chunks)
                    logger.info(f"Loaded {len(chunks)} chunks from {chunk_file.name}")
                else:
                    logger.warning(f"Unexpected format in {chunk_file.name}")
        except Exception as e:
            logger.error(f"Error loading {chunk_file.name}: {e}")

    logger.info(f"Total chunks loaded: {len(all_chunks)}")
    return all_chunks


def generate_embeddings(
    texts: List[str], model: str = "text-embedding-3-small"
) -> List[List[float]]:
    """
    Generate OpenAI embeddings for a batch of texts.

    Args:
        texts: List of text strings to embed
        model: Embedding model name (default: text-embedding-3-small)

    Returns:
        List of embedding vectors
    """
    logger.info(f"Generating dense embeddings for {len(texts)} texts using {model}")
    embeddings = []
    
    # Initialize OpenAI client (new API)
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Process in batches to avoid rate limits
    batch_size = 100
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        try:
            response = client.embeddings.create(model=model, input=batch)
            batch_embeddings = [item.embedding for item in response.data]
            embeddings.extend(batch_embeddings)
            logger.info(f"Generated dense embeddings for batch {i // batch_size + 1}")
        except Exception as e:
            logger.error(f"Error generating embeddings for batch {i // batch_size + 1}: {e}")
            raise

    return embeddings


def generate_sparse_embeddings(texts: List[str]) -> List[SparseVector]:
    """
    Generate sparse BM25 embeddings using FastEmbed.

    Args:
        texts: List of text strings to embed

    Returns:
        List of SparseVector objects for Qdrant
    """
    logger.info(f"Generating sparse embeddings for {len(texts)} texts using FastEmbed BM25")
    sparse_model = SparseTextEmbedding(model_name="Qdrant/bm25")
    
    sparse_vectors = []
    # FastEmbed processes in batches - iterate through embeddings
    try:
        # Generate embeddings (FastEmbed handles batching internally)
        embeddings = list(sparse_model.embed(texts))
        for embedding in embeddings:
            # Convert to Qdrant SparseVector format
            sparse_obj = embedding.as_object()
            sparse_vector = SparseVector(
                indices=sparse_obj["indices"],
                values=sparse_obj["values"],
            )
            sparse_vectors.append(sparse_vector)
    except Exception as e:
        logger.error(f"Error generating sparse embeddings: {e}")
        raise
    
    logger.info(f"Generated {len(sparse_vectors)} sparse embeddings")
    return sparse_vectors


def prepare_points(
    chunks: List[Dict[str, Any]],
    embeddings: List[List[float]],
    sparse_vectors: List[SparseVector],
) -> List[PointStruct]:
    """
    Prepare PointStruct objects for Qdrant upsert with both dense and sparse vectors.

    Args:
        chunks: List of chunk dictionaries
        embeddings: List of dense embedding vectors
        sparse_vectors: List of sparse embedding vectors

    Returns:
        List of PointStruct objects
    """
    points = []
    for chunk, embedding, sparse_vector in zip(chunks, embeddings, sparse_vectors):
        # Extract metadata
        metadata = chunk.get("metadata", {})
        chunk_id = chunk.get("chunk_id", "")

        # Convert chunk_id to a stable numeric ID
        # Use MD5 hash of chunk_id to ensure consistency across runs
        hash_obj = hashlib.md5(chunk_id.encode("utf-8"))
        # Convert to int64 (positive value)
        point_id = int(hash_obj.hexdigest()[:15], 16) % (2**63)

        # Prepare payload with all metadata
        payload = {
            "chunk_id": chunk_id,
            "text": chunk.get("text", ""),
            "source_type": metadata.get("source_type"),
            "organization": metadata.get("organization"),
            "file_name": metadata.get("file_name"),
            "file_path": metadata.get("file_path"),
            "clinical_area": metadata.get("clinical_area"),
            "last_updated": metadata.get("last_updated"),
            "sortable_date": metadata.get("sortable_date"),
            "priority_score": metadata.get("priority_score", 0.5),
            "is_presentation": metadata.get("is_presentation", False),
            "context_header": metadata.get("context_header", ""),
        }

        # Create PointStruct with both dense and sparse vectors
        # Both vectors go in the 'vector' dict - dense as List[float], sparse as SparseVector
        point = PointStruct(
            id=point_id,
            vector={
                "dense": embedding,
                SPARSE_VECTOR_NAME: sparse_vector,
            },
            payload=payload,
        )
        points.append(point)

    return points


def main() -> None:
    """Main function to upsert chunks to Qdrant."""
    # Initialize OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    openai.api_key = api_key

    # Initialize Qdrant vector store
    vector_store = QdrantVectorStore()

    # Create collection (recreate if exists to support sparse vectors)
    if vector_store.collection_exists():
        logger.info("Collection exists. Recreating to support sparse vectors...")
        vector_store.create_collection(recreate=True)
    else:
        logger.info("Creating new collection...")
        vector_store.create_collection(recreate=False)

    # Load chunk files
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data" / "processed"
    chunks = load_chunk_files(data_dir)

    if not chunks:
        logger.error("No chunks found to upsert")
        return

    # Generate embeddings (dense and sparse)
    texts = [chunk["text"] for chunk in chunks]
    logger.info("Generating dense embeddings...")
    embeddings = generate_embeddings(texts)
    logger.info("Generating sparse embeddings...")
    sparse_embeddings = generate_sparse_embeddings(texts)

    # Prepare points with both dense and sparse vectors
    logger.info("Preparing points for upsert...")
    points = prepare_points(chunks, embeddings, sparse_embeddings)

    # Upsert to Qdrant in batches
    batch_size = 100
    total_batches = (len(points) + batch_size - 1) // batch_size

    logger.info(f"Upserting {len(points)} points in {total_batches} batches...")
    for i in range(0, len(points), batch_size):
        batch = points[i : i + batch_size]
        batch_num = i // batch_size + 1
        logger.info(f"Upserting batch {batch_num}/{total_batches} ({len(batch)} points)")
        vector_store.upsert_points(batch, wait=True)

    # Get collection stats
    stats = vector_store.get_collection_stats()
    logger.info(f"Collection stats: {stats}")

    logger.info("Upsert complete!")


if __name__ == "__main__":
    main()


"""FastAPI backend for NEPPA - Expert Patient Policy Assistant."""

import logging
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.engine.rag_engine import RAGEngine
from src.utils.audit_logger import log_query

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="NEPPA API",
    description="NHS Expert Patient Policy Assistant - RAG-based policy query engine",
    version="1.0.0",
)

# Configure CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG Engine (singleton pattern)
rag_engine = None


def get_rag_engine() -> RAGEngine:
    """Get or create RAG engine instance."""
    global rag_engine
    if rag_engine is None:
        logger.info("Initializing RAG Engine...")
        rag_engine = RAGEngine()
    return rag_engine


# Pydantic models for request/response validation
class QueryRequest(BaseModel):
    """Request model for query endpoint."""

    query: str = Field(..., description="User query string", min_length=1, max_length=1000)
    limit: int = Field(default=10, description="Maximum number of chunks to retrieve", ge=1, le=50)


class SourceMetadata(BaseModel):
    """Source metadata for citations."""

    source_id: int
    file_name: str
    organization: str
    source_type: str
    last_updated: str
    year: str | None
    reference_code: str | None
    citation_key: str
    clinical_area: str


class ChunkScore(BaseModel):
    """Chunk retrieval score information with detailed scoring breakdown."""

    chunk_id: str
    score: float = Field(..., description="Final boosted score (0.7 * similarity + 0.2 * priority + 0.1 * recency)")
    original_score: float | None = Field(None, description="Similarity score from hybrid search (70% weight)")
    priority_score: float | None = Field(None, description="Priority score from metadata (20% weight)")
    recency_score: float | None = Field(None, description="Recency score based on document age (10% weight)")
    source_type: str
    organization: str
    file_name: str
    chunk_text: str = Field(..., description="The actual text content of the chunk")
    file_path: str | None = Field(None, description="Relative path to the source file")
    context_header: str | None = Field(None, description="Section heading for this chunk")


class ThoughtTrace(BaseModel):
    """Expert reasoning trace information."""

    expanded_terms: List[str] = Field(..., description="Query expansion terms")
    chunk_scores: List[ChunkScore] = Field(..., description="Retrieved chunks with scores")


class QueryResponse(BaseModel):
    """Response model for query endpoint."""

    answer: str = Field(..., description="Generated expert response")
    sources: List[SourceMetadata] = Field(..., description="Source citations")
    thought_trace: ThoughtTrace = Field(..., description="Query expansion and retrieval trace")


@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint for health check."""
    return {"status": "healthy", "service": "NEPPA API"}


@app.get("/health")
async def health() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    """
    Process a user query through the RAG pipeline.

    Args:
        request: Query request with user query and optional limit

    Returns:
        QueryResponse with answer, sources, and thought trace
    """
    try:
        logger.info(f"Received query: '{request.query}'")
        
        # Get RAG engine instance
        engine = get_rag_engine()
        
        # Process query through RAG pipeline
        result = engine.query(query=request.query, limit=request.limit)
        
        # Extract response components
        answer = result.get("response", "")
        sources_data = result.get("sources", [])
        chunks = result.get("chunks", [])
        expanded_terms = result.get("expanded_terms", [])
        
        # Format sources metadata
        sources = []
        for src in sources_data:
            # Ensure all required fields are strings (handle None values)
            last_updated = src.get("last_updated") or "Unknown"
            if last_updated is None:
                last_updated = "Unknown"
            
            sources.append(
                SourceMetadata(
                    source_id=src.get("source_id", 0),
                    file_name=src.get("file_name", "Unknown"),
                    organization=src.get("organization", "Unknown"),
                    source_type=src.get("source_type", "Unknown"),
                    last_updated=str(last_updated),  # Ensure it's a string
                    year=src.get("year"),
                    reference_code=src.get("reference_code"),
                    citation_key=src.get("citation_key", ""),
                    clinical_area=src.get("clinical_area", "Unknown"),
                )
            )
        
        # Format chunk scores for thought trace with detailed scoring
        chunk_scores = []
        for chunk in chunks:
            payload = chunk.get("payload", {})
            chunk_scores.append(
                ChunkScore(
                    chunk_id=payload.get("chunk_id", "unknown"),
                    score=round(chunk.get("score", 0.0), 4),
                    original_score=round(chunk.get("original_score", 0.0), 4) if chunk.get("original_score") is not None else None,
                    priority_score=round(chunk.get("priority_score", 0.0), 4) if chunk.get("priority_score") is not None else None,
                    recency_score=round(chunk.get("recency_score", 0.0), 4) if chunk.get("recency_score") is not None else None,
                    source_type=payload.get("source_type", "Unknown"),
                    organization=payload.get("organization", "Unknown"),
                    file_name=payload.get("file_name", "Unknown"),
                    chunk_text=payload.get("text", ""),
                    file_path=payload.get("file_path"),
                    context_header=payload.get("context_header"),
                )
            )
        
        # Create thought trace
        thought_trace = ThoughtTrace(
            expanded_terms=expanded_terms,
            chunk_scores=chunk_scores,
        )
        
        # Build response
        response = QueryResponse(
            answer=answer,
            sources=sources,
            thought_trace=thought_trace,
        )
        
        logger.info(f"Query processed successfully. Retrieved {len(sources)} sources.")
        
        # Log query to audit trail
        try:
            log_query(
                query=request.query,
                response=answer,
                chunks=chunks,
                expanded_terms=expanded_terms,
                metadata={"limit": request.limit, "num_sources": len(sources)},
            )
        except Exception as e:
            logger.warning(f"Failed to log query to audit trail: {e}")
        
        return response
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Error processing query: {e}\n{error_trace}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing query: {str(e)}. Check server logs for details."
        )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(app, host="0.0.0.0", port=8000)


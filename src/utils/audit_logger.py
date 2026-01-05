"""Audit trail logging for query evaluation and analysis.

This module provides functionality to log all queries, retrieved chunks, and responses
for evaluation purposes (Sprint 7: RAGAS Evaluation).
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Set up logging
logger = logging.getLogger(__name__)

# Audit trail file path
AUDIT_TRAIL_FILE = Path("logs") / "audit_trail.json"


def ensure_logs_directory() -> None:
    """Ensure the logs directory exists."""
    AUDIT_TRAIL_FILE.parent.mkdir(parents=True, exist_ok=True)


def load_audit_trail() -> List[Dict[str, Any]]:
    """
    Load existing audit trail from JSON file.
    
    Returns:
        List of audit trail entries
    """
    ensure_logs_directory()
    
    if not AUDIT_TRAIL_FILE.exists():
        return []
    
    try:
        with open(AUDIT_TRAIL_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.warning(f"Error loading audit trail: {e}. Starting with empty trail.")
        return []


def save_audit_trail(entries: List[Dict[str, Any]]) -> None:
    """
    Save audit trail to JSON file.
    
    Args:
        entries: List of audit trail entries to save
    """
    ensure_logs_directory()
    
    try:
        with open(AUDIT_TRAIL_FILE, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2, ensure_ascii=False)
    except IOError as e:
        logger.error(f"Error saving audit trail: {e}")


def log_query(
    query: str,
    response: str,
    chunks: List[Dict[str, Any]],
    expanded_terms: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Log a query and its response to the audit trail.
    
    Args:
        query: User query string
        response: Generated response text
        chunks: List of retrieved chunks with scores and payloads
        expanded_terms: Optional list of query expansion terms
        metadata: Optional additional metadata (e.g., timestamp, latency)
    """
    try:
        # Load existing audit trail
        audit_trail = load_audit_trail()
        
        # Format chunks for logging (extract relevant fields)
        formatted_chunks = []
        for chunk in chunks:
            payload = chunk.get("payload", {})
            formatted_chunk = {
                "chunk_id": payload.get("chunk_id", "unknown"),
                "score": chunk.get("score", 0.0),
                "original_score": chunk.get("original_score"),
                "priority_score": chunk.get("priority_score"),
                "recency_score": chunk.get("recency_score"),
                "file_name": payload.get("file_name", "Unknown"),
                "source_type": payload.get("source_type", "Unknown"),
                "organization": payload.get("organization", "Unknown"),
                "context_header": payload.get("context_header"),
                "text_preview": payload.get("text", "")[:200] + "..." if payload.get("text") else "",  # First 200 chars
            }
            formatted_chunks.append(formatted_chunk)
        
        # Create audit entry
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "query": query,
            "response": response,
            "num_chunks": len(chunks),
            "chunks": formatted_chunks,
            "expanded_terms": expanded_terms or [],
            "metadata": metadata or {},
        }
        
        # Append to audit trail
        audit_trail.append(entry)
        
        # Save updated audit trail
        save_audit_trail(audit_trail)
        
        logger.info(f"Logged query to audit trail: '{query[:50]}...' ({len(chunks)} chunks)")
        
    except Exception as e:
        logger.error(f"Error logging query to audit trail: {e}")


def get_audit_trail_stats() -> Dict[str, Any]:
    """
    Get statistics from the audit trail.
    
    Returns:
        Dictionary with audit trail statistics
    """
    audit_trail = load_audit_trail()
    
    if not audit_trail:
        return {
            "total_queries": 0,
            "total_chunks_retrieved": 0,
            "avg_chunks_per_query": 0,
        }
    
    total_queries = len(audit_trail)
    total_chunks = sum(entry.get("num_chunks", 0) for entry in audit_trail)
    
    return {
        "total_queries": total_queries,
        "total_chunks_retrieved": total_chunks,
        "avg_chunks_per_query": total_chunks / total_queries if total_queries > 0 else 0,
        "first_query": audit_trail[0].get("timestamp") if audit_trail else None,
        "last_query": audit_trail[-1].get("timestamp") if audit_trail else None,
    }


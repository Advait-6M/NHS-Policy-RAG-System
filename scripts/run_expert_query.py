"""Test script for Sprint 3: Expert Reasoning Engine.

This script tests the complete RAG pipeline end-to-end with a sample query.
"""

import sys
from pathlib import Path

# Force unbuffered output for real-time display
# This ensures output is visible in real-time, not just at the end
import os
os.environ['PYTHONUNBUFFERED'] = '1'

# Add src to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

from src.engine.rag_engine import RAGEngine

# Load environment variables
load_dotenv()


def main() -> None:
    """Test the expert query pipeline."""
    print("=" * 70, flush=True)
    print("NEPPA Sprint 3: Expert Reasoning Engine - Test Query", flush=True)
    print("=" * 70, flush=True)
    print(flush=True)
    
    # Initialize RAG Engine
    print("Initializing RAG Engine...")
    try:
        engine = RAGEngine()
        print("✓ RAG Engine initialized")
    except Exception as e:
        print(f"✗ Error initializing RAG Engine: {e}")
        return
    
    print()
    
    # Test query
    test_query = "What is the policy for using SGLT2 inhibitors like Dapagliflozin for heart failure?"
    print(f"Test Query: {test_query}")
    print()
    print("-" * 70)
    print()
    
    # Execute query
    print("Processing query...")
    print("  → Expanding query...")
    print("  → Retrieving relevant chunks...")
    print("  → Formatting context...")
    print("  → Generating expert response...")
    print()
    
    try:
        result = engine.query(test_query, limit=10)
        
        # Display results
        print("=" * 70)
        print("QUERY EXPANSION")
        print("=" * 70)
        expanded_terms = result.get("expanded_terms", [])
        for i, term in enumerate(expanded_terms, 1):
            print(f"  {i}. {term}")
        print()
        
        print("=" * 70)
        print("RETRIEVED CHUNKS")
        print("=" * 70)
        chunks = result.get("chunks", [])
        print(f"Total chunks retrieved: {len(chunks)}")
        print()
        
        for i, chunk in enumerate(chunks[:5], 1):  # Show first 5
            payload = chunk.get("payload", {})
            score = chunk.get("score", 0.0)
            print(f"Chunk {i} (Score: {score:.4f}):")
            print(f"  Source: {payload.get('source_type', 'Unknown')} | {payload.get('organization', 'Unknown')}")
            print(f"  Document: {payload.get('file_name', 'Unknown')}")
            print(f"  Date: {payload.get('last_updated', 'Unknown')}")
            text_preview = payload.get('text', '')[:150]
            print(f"  Preview: {text_preview}...")
            print()
        
        if len(chunks) > 5:
            print(f"  ... and {len(chunks) - 5} more chunks")
            print()
        
        print("=" * 70)
        print("EXPERT RESPONSE")
        print("=" * 70)
        response = result.get("response", "")
        print(response)
        print()
        
        print("=" * 70)
        print("SOURCES")
        print("=" * 70)
        sources = result.get("sources", [])
        for source in sources:
            print(f"  [Source {source['source_id']}]")
            print(f"    Document: {source['file_name']}")
            print(f"    Organization: {source['organization']}")
            print(f"    Authority: {source['source_type']}")
            print(f"    Date: {source['last_updated']}")
            print(f"    Clinical Area: {source['clinical_area']}")
            print()
        
        # Validation checks
        print("=" * 70)
        print("VALIDATION")
        print("=" * 70)
        
        # Check if CPICS document is prioritized
        local_chunks = [c for c in chunks if c.get("payload", {}).get("source_type") == "Local"]
        national_chunks = [c for c in chunks if c.get("payload", {}).get("source_type") == "National"]
        
        print(f"✓ Local (CPICS) chunks: {len(local_chunks)}")
        print(f"✓ National (NICE) chunks: {len(national_chunks)}")
        
        if local_chunks and chunks:
            top_chunk_source = chunks[0].get("payload", {}).get("source_type")
            if top_chunk_source == "Local":
                print("✓ Top chunk is Local (CPICS) - Priority hierarchy working!")
            else:
                print(f"⚠ Top chunk is {top_chunk_source} (expected Local)")
        
        # Check for citations
        if "[Source" in response or "[SOURCE" in response:
            print("✓ Response contains citations")
        else:
            print("⚠ Response may be missing citations")
        
        # Check for safety refusal (if no relevant chunks)
        if "cannot find specific guidance" in response.lower():
            print("✓ Safety refusal triggered (no relevant context found)")
        elif chunks:
            print("✓ Response generated from retrieved context")
        
        print()
        print("=" * 70)
        print("Test Complete!")
        print("=" * 70)
        
    except Exception as e:
        print(f"✗ Error processing query: {e}")
        import traceback
        traceback.print_exc()
        return


if __name__ == "__main__":
    main()


"""Test script to verify RAG engine with multiple queries."""

import sys
from pathlib import Path

# Add src to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.engine.rag_engine import RAGEngine

# Load environment variables
load_dotenv()

# Force unbuffered output
import os
os.environ['PYTHONUNBUFFERED'] = '1'


def test_query(engine: RAGEngine, query: str, query_num: int) -> None:
    """Test a single query and display results."""
    print("=" * 80)
    print(f"TEST QUERY {query_num}: {query}")
    print("=" * 80)
    print()
    
    try:
        result = engine.query(query, limit=10)
        
        # Display response
        response = result.get("response", "")
        print("RESPONSE:")
        print("-" * 80)
        print(response)
        print()
        
        # Display sources
        sources = result.get("sources", [])
        print(f"SOURCES ({len(sources)} unique documents):")
        print("-" * 80)
        for source in sources[:5]:  # Show first 5
            citation_key = source.get("citation_key", "N/A")
            print(f"  {citation_key}: {source.get('file_name', 'Unknown')}")
        if len(sources) > 5:
            print(f"  ... and {len(sources) - 5} more sources")
        print()
        
        # Quick validation
        chunks = result.get("chunks", [])
        local_count = sum(1 for c in chunks if c.get("payload", {}).get("source_type") == "Local")
        national_count = sum(1 for c in chunks if c.get("payload", {}).get("source_type") == "National")
        
        print("VALIDATION:")
        print(f"  ✓ Chunks retrieved: {len(chunks)}")
        print(f"  ✓ Local sources: {local_count}")
        print(f"  ✓ National sources: {national_count}")
        
        # Check for reference codes in citations
        has_nice_ref = any("NG" in source.get("citation_key", "") or "TA" in source.get("citation_key", "") 
                          for source in sources if source.get("organization") == "NICE")
        if has_nice_ref:
            print(f"  ✓ NICE reference codes extracted")
        
        # Check for Harvard citations
        has_harvard = "(" in response and ")" in response and any(
            org in response for org in ["CPICS", "NICE", "NHS England"]
        )
        if has_harvard:
            print(f"  ✓ Harvard-style citations present")
        
        # Check for bibliography
        has_bibliography = "Bibliography" in response or "bibliography" in response.lower()
        if has_bibliography:
            print(f"  ✓ Bibliography included")
        
        # Check for safety disclaimer
        has_disclaimer = "does not replace professional clinical judgment" in response.lower()
        if has_disclaimer:
            print(f"  ✓ Safety disclaimer present")
        
        print()
        
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        print()


def main() -> None:
    """Run multiple test queries."""
    print("=" * 80)
    print("NEPPA Sprint 3: Multiple Query Test Suite")
    print("=" * 80)
    print()
    
    # Initialize RAG Engine
    print("Initializing RAG Engine...")
    try:
        engine = RAGEngine()
        print("✓ RAG Engine initialized\n")
    except Exception as e:
        print(f"✗ Error initializing RAG Engine: {e}")
        return
    
    # Test queries covering different scenarios
    test_queries = [
        {
            "query": "What is the policy for using SGLT2 inhibitors like Dapagliflozin for heart failure?",
            "description": "Specific drug query with Local + National sources"
        },
        {
            "query": "What are the eligibility criteria for continuous glucose monitoring?",
            "description": "Technology/device query"
        },
        {
            "query": "What are my rights if my surgery is cancelled?",
            "description": "Patient rights query (Legal/Constitution sources)"
        },
        {
            "query": "How do I request funding for a non-standard treatment?",
            "description": "IFR process query (Governance sources)"
        },
        {
            "query": "What is the policy for Tirzepatide in type 2 diabetes?",
            "description": "Specific medication query"
        },
        {
            "query": "What is the weather today?",
            "description": "Out-of-scope query (should trigger safety refusal)"
        }
    ]
    
    print(f"Running {len(test_queries)} test queries...")
    print()
    
    for i, test in enumerate(test_queries, 1):
        print(f"[Query {i}/{len(test_queries)}] {test['description']}")
        test_query(engine, test["query"], i)
        print()
    
    print("=" * 80)
    print("TEST SUITE COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()


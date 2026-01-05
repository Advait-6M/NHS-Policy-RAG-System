"""Debug script to test RAG engine query step by step."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.engine.rag_engine import RAGEngine

# Load environment
load_dotenv()

print("=" * 80)
print("RAG Engine Query Debugging")
print("=" * 80)

try:
    print("\n1. Initializing RAG Engine...")
    engine = RAGEngine()
    print("✓ RAG Engine initialized")
    
    print("\n2. Testing query expansion...")
    query = "What is the policy for using SGLT2 inhibitors like Dapagliflozin for heart failure?"
    expanded_terms = engine.expand_query(query)
    print(f"✓ Query expanded to {len(expanded_terms)} terms: {expanded_terms}")
    
    print("\n3. Testing embedding generation (first term)...")
    print(f"   Generating embedding for: '{expanded_terms[0]}'")
    dense_vector = engine._generate_dense_embedding(expanded_terms[0])
    print(f"✓ Dense embedding generated (length: {len(dense_vector)})")
    
    print("\n4. Testing sparse embedding generation...")
    sparse_vector = engine._generate_sparse_embedding(expanded_terms[0])
    print(f"✓ Sparse embedding generated (indices: {len(sparse_vector.indices)}, values: {len(sparse_vector.values)})")
    
    print("\n5. Testing full retrieval (limit=3)...")
    chunks = engine.retrieve(query, limit=3, use_expansion=True)
    print(f"✓ Retrieved {len(chunks)} chunks")
    
    print("\n6. Testing full query...")
    result = engine.query(query, limit=3)
    print(f"✓ Query completed successfully")
    print(f"   Response length: {len(result.get('response', ''))} chars")
    print(f"   Chunks: {len(result.get('chunks', []))}")
    
    print("\n" + "=" * 80)
    print("✓ All steps completed successfully!")
    print("=" * 80)
    
except Exception as e:
    print(f"\n✗ ERROR at step: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


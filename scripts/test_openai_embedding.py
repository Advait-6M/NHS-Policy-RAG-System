"""Quick test script to debug OpenAI embedding API calls."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load environment
load_dotenv()

# Test embedding generation with timeout
print("Testing OpenAI Embedding API...")
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("✗ ERROR: OPENAI_API_KEY not set")
    sys.exit(1)

print(f"✓ API Key found (length: {len(api_key)})")

# Create client with explicit timeout
client = OpenAI(api_key=api_key, timeout=30.0)
print("✓ OpenAI client created with 30s timeout")

try:
    print("\nCalling embeddings.create()...")
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=["test query for debugging"]
    )
    print(f"✓ Success! Generated embedding of length: {len(response.data[0].embedding)}")
except Exception as e:
    print(f"\n✗ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✓ All tests passed!")


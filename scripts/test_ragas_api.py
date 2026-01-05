"""Test script to understand Ragas 0.4.2 API."""

import os
from dotenv import load_dotenv
from openai import OpenAI
from ragas.metrics.collections import Faithfulness, AnswerRelevancy
from ragas.llms import llm_factory
from ragas.embeddings import OpenAIEmbeddings

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

print("Testing Ragas 0.4.2 API...")
print("\n1. Creating LLM and embeddings...")
llm = llm_factory("gpt-4o", client=client)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small", client=client)
print("✓ Created")

print("\n2. Testing Faithfulness() - no params...")
try:
    f1 = Faithfulness()
    print("✓ Faithfulness() works")
except Exception as e:
    print(f"✗ Faithfulness() failed: {e}")

print("\n3. Testing Faithfulness(llm=llm)...")
try:
    f2 = Faithfulness(llm=llm)
    print("✓ Faithfulness(llm=llm) works")
except Exception as e:
    print(f"✗ Faithfulness(llm=llm) failed: {e}")

print("\n4. Testing AnswerRelevancy() - no params...")
try:
    a1 = AnswerRelevancy()
    print("✓ AnswerRelevancy() works")
except Exception as e:
    print(f"✗ AnswerRelevancy() failed: {e}")

print("\n5. Testing AnswerRelevancy(llm=llm, embeddings=embeddings)...")
try:
    a2 = AnswerRelevancy(llm=llm, embeddings=embeddings)
    print("✓ AnswerRelevancy(llm=llm, embeddings=embeddings) works")
except Exception as e:
    print(f"✗ AnswerRelevancy(llm=llm, embeddings=embeddings) failed: {e}")


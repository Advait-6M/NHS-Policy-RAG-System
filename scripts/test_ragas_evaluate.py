"""Test script to understand Ragas 0.4.2 evaluate() function."""

import os
from dotenv import load_dotenv
from openai import OpenAI
from datasets import Dataset
from ragas import evaluate
from ragas.metrics.collections import Faithfulness, AnswerRelevancy
from ragas.llms import llm_factory
from ragas.embeddings import OpenAIEmbeddings

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

print("Testing Ragas 0.4.2 evaluate() function...")
print("\n1. Creating LLM and embeddings...")
llm = llm_factory("gpt-4o", client=client)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small", client=client)
print("✓ Created")

print("\n2. Creating metrics...")
metrics = [
    Faithfulness(llm=llm),
    AnswerRelevancy(llm=llm, embeddings=embeddings),
]
print(f"✓ Created {len(metrics)} metrics")

print("\n3. Checking metric types...")
for i, metric in enumerate(metrics):
    print(f"   Metric {i+1}: {type(metric).__name__} - {type(metric)}")

print("\n4. Creating minimal test dataset...")
dataset_dict = {
    "question": ["test question"],
    "answer": ["test answer"],
    "contexts": [["test context"]],
    "ground_truth": ["test ground truth"],
}
dataset = Dataset.from_dict(dataset_dict)
print("✓ Dataset created")

print("\n5. Testing evaluate() with metrics...")
try:
    result = evaluate(dataset=dataset, metrics=metrics)
    print("✓ evaluate() succeeded!")
except Exception as e:
    print(f"✗ evaluate() failed: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()


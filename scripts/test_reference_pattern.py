"""Test the reference pattern from Ragas 0.4.2 PyPI documentation."""

import asyncio
from ragas.metrics.collections import AspectCritic
from ragas.llms import llm_factory
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

async def test_reference():
    # Setup your LLM - test both patterns
    print("Testing llm_factory patterns...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set")
        return
    
    # Try without client first (as in reference)
    try:
        print("\n1. Testing llm_factory('gpt-4o') without client...")
        llm = llm_factory("gpt-4o")
        print("   ✓ Success without client!")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        # Try with client
        print("\n2. Testing llm_factory('gpt-4o', client=client) with client...")
        client = OpenAI(api_key=api_key)
        llm = llm_factory("gpt-4o", client=client)
        print("   ✓ Success with client!")
    
    # Create a metric (as in reference)
    print("\n3. Creating AspectCritic metric...")
    metric = AspectCritic(
        name="summary_accuracy",
        definition="Verify if the summary is accurate and captures key information.",
        llm=llm
    )
    print("   ✓ Metric created!")
    
    # Evaluate (as in reference)
    print("\n4. Running evaluation...")
    test_data = {
        "user_input": "summarise given text\nThe company reported an 8% rise in Q3 2024, driven by strong performance in the Asian market. Sales in this region have significantly contributed to the overall growth. Analysts attribute this success to strategic marketing and product localization. The positive trend in the Asian market is expected to continue into the next quarter.",
        "response": "The company experienced an 8% increase in Q3 2024, largely due to effective marketing strategies and product adaptation, with expectations of continued growth in the coming quarter.",
    }
    
    score = await metric.ascore(
        user_input=test_data["user_input"],
        response=test_data["response"]
    )
    print(f"   ✓ Evaluation complete!")
    print(f"\nScore: {score.value}")
    print(f"Reason: {score.reason}")

if __name__ == "__main__":
    asyncio.run(test_reference())


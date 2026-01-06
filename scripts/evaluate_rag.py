"""NEPPA Sprint 7: RAGAS Evaluation Framework (Windows Optimized)."""

# 1. WINDOWS PROTECTION: Absolute first lines
import nest_asyncio
nest_asyncio.apply()

import os
import sys
import json
import logging
import asyncio
import warnings
from pathlib import Path
from typing import Any, Dict, List
from dotenv import load_dotenv

# Suppress deprecation warnings for cleaner output
warnings.filterwarnings('ignore', category=DeprecationWarning)

# Ragas v0.3+ Optimized Imports (Direct imports to avoid collections hang)
print("[*] Loading evaluation libraries (first run may take 1-2 minutes)...", flush=True)
from ragas import evaluate
from ragas.metrics import faithfulness as Faithfulness
from ragas.metrics import answer_relevancy as AnswerRelevancy
from ragas.metrics import context_precision as ContextPrecision
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from datasets import Dataset
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
print("[OK] Libraries loaded successfully", flush=True)

# Project setup
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
from src.engine.rag_engine import RAGEngine

load_dotenv()

# No pre-warming needed with Langchain wrappers

# --- GOLDEN DATASET (Diabetes-Focused) ---
# Import diabetes-specific questions
from golden_questions_diabetes import get_golden_questions

# Load all diabetes questions, but we'll only use first 3 for quick testing
ALL_GOLDEN_QUESTIONS = get_golden_questions()

# For quick testing: use first 3 questions
# To run full evaluation: change to ALL_GOLDEN_QUESTIONS
GOLDEN_QUESTIONS = [
    {"question": q["question"], "ground_truth": q["ground_truth"]} 
    for q in ALL_GOLDEN_QUESTIONS  # Use all questions, slice in prepare_evaluation_data
]

def prepare_evaluation_data(engine: RAGEngine, num_questions: int) -> List[Dict[str, Any]]:
    """Prepare evaluation dataset by running queries through RAG engine."""
    evaluation_data = []
    subset = GOLDEN_QUESTIONS[:num_questions]
    print(f"\nGenerating answers for {len(subset)} questions via RAGEngine...", flush=True)
    
    for i, item in enumerate(subset, 1):
        print(f"  [{i}/{len(subset)}] {item['question'][:60]}...", flush=True)
        result = engine.query(item["question"])
        evaluation_data.append({
            "question": item["question"],
            "answer": result.get("response", ""),
            "contexts": [c.get("payload", {}).get("text", "") for c in result.get("chunks", [])],
            "ground_truth": item["ground_truth"]
        })
    
    print(f"[OK] Prepared {len(evaluation_data)} evaluation samples\n", flush=True)
    return evaluation_data

def calculate_ragas_metrics(evaluation_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    print("[*] Initializing Evaluation Engine...", flush=True)
    
    # Windows SSL Fix: Create custom HTTP client with disabled SSL verification
    import httpx
    http_client = httpx.Client(verify=False, timeout=30.0)
    async_http_client = httpx.AsyncClient(verify=False, timeout=30.0)
    
    # Use Langchain with Ragas wrappers (with custom HTTP clients to avoid Windows SSL hang)
    langchain_llm = ChatOpenAI(
        model="gpt-4o", 
        temperature=0,
        http_client=http_client,
        http_async_client=async_http_client
    )
    langchain_embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        http_client=http_client,
        http_async_client=async_http_client
    )
    
    evaluator_llm = LangchainLLMWrapper(langchain_llm)
    evaluator_embeddings = LangchainEmbeddingsWrapper(langchain_embeddings)
    
    print("  [OK] LLM and embeddings initialized", flush=True)

    dataset = Dataset.from_dict({
        "question": [item["question"] for item in evaluation_data],
        "answer": [item["answer"] for item in evaluation_data],
        "contexts": [item["contexts"] for item in evaluation_data],
        "ground_truth": [item["ground_truth"] for item in evaluation_data],
    })
    
    print("  [OK] Dataset created", flush=True)

    # Use pre-instantiated metric objects and set LLM/embeddings
    Faithfulness.llm = evaluator_llm
    AnswerRelevancy.llm = evaluator_llm
    AnswerRelevancy.embeddings = evaluator_embeddings
    ContextPrecision.llm = evaluator_llm
    
    metrics = [Faithfulness, AnswerRelevancy, ContextPrecision]
    
    print("  [OK] Metrics configured", flush=True)

    print("\n[*] Calculating RAGAS scores (this may take 1-2 minutes)...", flush=True)
    # allow_nest_asyncio is mandatory for the nest_asyncio.apply() to work
    try:
        print("  [DEBUG] Starting evaluate() call...", flush=True)
        result = evaluate(
            dataset=dataset, 
            metrics=metrics, 
            allow_nest_asyncio=True
        )
        print("  [DEBUG] evaluate() completed successfully", flush=True)
        return result
    except KeyboardInterrupt:
        print("\n  [DEBUG] KeyboardInterrupt caught during evaluate()", flush=True)
        raise
    except Exception as e:
        print(f"\n  [DEBUG] Exception during evaluate(): {type(e).__name__}: {e}", flush=True)
        import traceback
        traceback.print_exc()
        raise

def print_summary(results: Any, num_questions: int = 1) -> None:
    """Print evaluation results summary."""
    print("\n" + "=" * 80)
    print(f"RAGAS EVALUATION RESULTS ({num_questions} Questions)")
    print("=" * 80)
    
    # Convert to pandas for easier display
    results_df = results.to_pandas()
    
    # Identify metric columns (numeric columns that aren't input/output fields)
    metric_columns = [col for col in results_df.columns 
                     if col not in ["question", "answer", "contexts", "ground_truth", "reference"]
                     and results_df[col].dtype in ['float64', 'float32', 'int64', 'int32']]
    
    # Calculate mean scores
    print("\nMean Scores (0.0 to 1.0):")
    print("-" * 80)
    for col in metric_columns:
        mean_score = results_df[col].mean()
        score_str = f"{mean_score:.4f}"
        
        # Color coding
        if mean_score >= 0.85:
            status = "[OK] EXCELLENT"
        elif mean_score >= 0.70:
            status = "[!] GOOD"
        else:
            status = "[X] NEEDS IMPROVEMENT"
        
        metric_name = col.replace("_", " ").title()
        print(f"  {metric_name:20s}: {score_str:8s}  {status}")
    
    print("-" * 80)
    
    # Overall assessment
    if metric_columns:
        avg_score = sum(results_df[col].mean() for col in metric_columns) / len(metric_columns)
        print(f"\nOverall Average Score: {avg_score:.4f}")
        if avg_score >= 0.85:
            print("Overall Assessment: EXCELLENT")
        elif avg_score >= 0.70:
            print("Overall Assessment: GOOD")
        else:
            print("Overall Assessment: NEEDS IMPROVEMENT")
    
    print("\n[OK] Sprint 7: Accuracy Audit Complete.")
    print("=" * 80 + "\n")
    
    # Save detailed results to JSON
    output_path = project_root / "logs" / "ragas_evaluation_results.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert results to JSON-serializable format
    results_dict = results_df.to_dict(orient="records")
    summary_dict = {
        "num_questions": num_questions,
        "mean_scores": {col: float(results_df[col].mean()) for col in metric_columns},
        "detailed_results": results_dict
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary_dict, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Detailed results saved to: {output_path}\n")

if __name__ == "__main__":
    # MANDATORY: On Windows, you MUST protect the entry point 
    # to avoid the RLock pickling error
    try:
        print(f"\n[DEBUG] Python version: {sys.version}")
        import ragas
        print(f"[DEBUG] Ragas version: {ragas.__version__}\n", flush=True)
        
        engine = RAGEngine()
        # Quick evaluation with 3 questions for faster iteration
        # (Change to 10 for full evaluation before final reporting)
        num_questions = 10
        data = prepare_evaluation_data(engine, num_questions=num_questions)
        
        if data:
            print("[DEBUG] About to call calculate_ragas_metrics()", flush=True)
            results = calculate_ragas_metrics(data)
            print("[DEBUG] calculate_ragas_metrics() returned successfully", flush=True)
            print_summary(results, num_questions=num_questions)
    except KeyboardInterrupt:
        print("\n[!] [DEBUG] KeyboardInterrupt caught in main()")
        import traceback
        print("Traceback:")
        traceback.print_exc()
    except Exception as e:
        print(f"\n[X] Critical Error: {e}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
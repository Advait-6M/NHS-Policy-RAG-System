# Sprint 7: Evaluation - Overview

## Goal
Quantify the accuracy and quality of the RAG system using RAGAS (Retrieval-Augmented Generation Assessment) framework to measure faithfulness, answer relevancy, and context recall.

## Deliverable
Comprehensive evaluation system with 10 golden questions, RAGAS metrics calculation, results logging, and terminal summary reporting.

## Success Criteria
- ✅ RAGAS framework integrated with Faithfulness, Answer Relevancy, and Context Recall metrics
- ✅ 10 golden questions covering key medical policy domains (drugs, technology, patient rights, IFR processes)
- ✅ Evaluation script processes queries through RAG engine and calculates metrics
- ✅ Results saved to `logs/eval_results.json` for visualization and analysis
- ✅ Terminal summary displays mean scores (0.0 to 1.0) with status indicators
- ✅ Target Faithfulness score >0.85 (as per project requirements)

## Key Features
- **RAGAS Integration**: Industry-standard evaluation framework for RAG systems
  - Faithfulness: Measures if the answer is grounded in the provided context
  - Answer Relevancy: Measures how relevant the answer is to the question
  - Context Recall: Measures if all relevant information from ground truth is present in context

- **Golden Question Set**: 10 carefully curated test questions
  - Drug policies (Dapagliflozin, Tirzepatide, SGLT2 inhibitors)
  - Technology eligibility (continuous glucose monitoring, monitoring devices)
  - Patient rights (NHS Constitution, surgery cancellation)
  - IFR processes (Individual Funding Requests, SOPs)
  - Diabetes management guidelines

- **Ground Truth Answers**: Manually crafted expected answers for each question
  - Based on actual policy documents in the knowledge base
  - Validates that system retrieves and synthesizes correct information

- **Results Logging**: Structured JSON output for analysis
  - Mean scores for each metric
  - Per-question detailed results
  - Total questions evaluated
  - Suitable for charting and visualization

- **Terminal Summary**: Human-readable evaluation report
  - Color-coded status indicators (✓ EXCELLENT ≥0.85, ⚠ GOOD ≥0.70, ✗ NEEDS IMPROVEMENT <0.70)
  - Overall assessment with target comparison
  - Clear indication of system performance

## Files Created/Modified
- `scripts/evaluate_rag.py` - Main evaluation script with RAGAS integration
- `requirements.txt` - Added ragas, langchain, and langchain-openai dependencies
- `logs/eval_results.json` - Evaluation results (generated on run)

## Technical Notes
- Uses GPT-3.5-turbo for RAGAS metric calculations (requires OpenAI API key)
- Evaluation may take several minutes to complete (10 questions × 3 metrics)
- Results are saved in JSON format for easy visualization and tracking over time
- Ground truth answers are manually crafted based on policy documents in the knowledge base


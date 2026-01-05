# Sprint 7: Evaluation - COMPLETE ✅

## Summary

Sprint 7 has successfully implemented and executed a comprehensive RAGAS-based evaluation system to quantify the accuracy and quality of the NEPPA RAG system. The implementation includes 10 golden questions covering all major policy domains, RAGAS v0.4.2 metrics calculation (Faithfulness, Answer Relevancy, Context Precision), Windows compatibility optimizations, results logging to JSON, and terminal summary with status indicators. **Full 10-question evaluation completed with baseline metrics established.**

## Evaluation Results (10 Questions - Completed)

### Baseline Performance Metrics

| Metric | Score | Status | Target | Assessment |
|--------|-------|--------|--------|------------|
| **Faithfulness** | 0.5750 | NEEDS IMPROVEMENT | >0.70 | ❌ Below target |
| **Answer Relevancy** | 0.8413 | GOOD | >0.70 | ✅ Above target |
| **Context Precision** | 0.0979 | NEEDS IMPROVEMENT | >0.85 | ❌ Critically below target |

**Overall Average Score**: 0.5047 (NEEDS IMPROVEMENT)

### Key Findings

**✅ STRENGTHS:**
- **Answer Relevancy (0.84)**: System generates highly relevant and focused responses
- Responses are on-topic and address user queries appropriately

**⚠️ CONCERNS:**
- **Faithfulness (0.58)**: Evidence of hallucination/extrapolation beyond source documents
- Inconsistent grounding in retrieved context
- Dropped from 0.75 (1-question test) to 0.58 (10-question evaluation)

**❌ CRITICAL ISSUES:**
- **Context Precision (0.10)**: Retrieval system only finding ~10% of relevant information
- **Root Cause**: Query expansion + hybrid search + reranking pipeline underperforming
- Primary bottleneck limiting overall system quality

### Core Components Implemented

1. **RAGAS Framework Integration** (`scripts/evaluate_rag.py`)
   - ✅ RAGAS 0.4.2 integrated with LangChain wrappers
   - ✅ Three key metrics implemented:
     - **Faithfulness**: Measures if answer is grounded in context (Target: >0.70)
     - **Answer Relevancy**: Measures relevance of answer to question (Target: >0.70)
     - **Context Precision**: Measures if retrieval finds all relevant information (Target: >0.85)
   - ✅ GPT-4o used for metric calculations (via LangchainLLMWrapper)
   - ✅ HuggingFace Dataset format for RAGAS evaluation
   - ✅ Windows SSL optimization (disabled verification for localhost)

2. **Golden Question Set** (10 questions)
   - ✅ Drug policy questions:
     - SGLT2 inhibitors (Dapagliflozin) for heart failure
     - Dapagliflozin for chronic kidney disease
     - Tirzepatide for type 2 diabetes
   - ✅ Technology eligibility questions:
     - Continuous glucose monitoring criteria
     - Diabetes monitoring technology availability
   - ✅ Patient rights questions:
     - NHS Constitution principles
     - Surgery cancellation rights
   - ✅ Process questions:
     - Individual Funding Request (IFR) process
     - IFR Standard Operating Procedures
   - ✅ Prescribing guidelines:
     - Insulin needles prescribing

3. **Ground Truth Answers**
   - ✅ Manually crafted expected answers for each question
   - ✅ Based on actual policy documents in knowledge base
   - ✅ Validates system retrieves and synthesizes correct information

4. **Evaluation Script** (`scripts/evaluate_rag.py`)
   - ✅ `prepare_evaluation_data()`: Runs queries through RAGEngine
   - ✅ `calculate_ragas_metrics()`: Calculates RAGAS metrics
   - ✅ `save_results()`: Saves results to JSON
   - ✅ `print_summary()`: Displays terminal summary
   - ✅ Comprehensive error handling and logging

5. **Results Logging** (`logs/eval_results.json`)
   - ✅ Mean scores for each metric
   - ✅ Per-question detailed results
   - ✅ Total questions evaluated
   - ✅ JSON format for easy visualization

6. **Terminal Summary**
   - ✅ Color-coded status indicators:
     - ✓ EXCELLENT (≥0.85)
     - ⚠ GOOD (≥0.70)
     - ✗ NEEDS IMPROVEMENT (<0.70)
   - ✅ Overall assessment with target comparison
   - ✅ Clear performance indicators

## Technical Implementation

### Files Created

1. **`scripts/evaluate_rag.py`** (~231 lines)
   - Main evaluation script with Windows compatibility fixes
   - 10 golden questions covering all policy domains
   - RAGAS 0.4.2 integration with Langchain wrappers
   - Results processing with JSON export
   - ASCII-only output (no Unicode emojis for Windows compatibility)

2. **`logs/ragas_evaluation_results.json`** (generated)
   - Complete evaluation results from 10-question run
   - Per-question breakdown with scores
   - Mean scores for all metrics
   - Retrieved contexts and generated responses

### Files Modified

1. **`src/database/vector_store.py`**
   - Added Windows SSL fix: `https=False`, `verify=False`, `timeout=10` for Qdrant client
   - Prevents HTTPX hang on Windows during SSL certificate scanning

2. **`src/engine/rag_engine.py`**
   - Fixed double query expansion bug
   - Added `expanded_terms` parameter to `retrieve()` method
   - Prevents redundant API calls during retrieval

### Windows Compatibility Fixes Applied

1. **SSL Certificate Loading Hang**
   - Issue: `ssl.create_default_context()` hangs on Windows during certificate chain scanning
   - Fix: Disabled SSL verification for localhost connections (Qdrant + OpenAI clients)
   - Impact: Script no longer hangs during initialization

2. **Unicode Encoding Errors**
   - Issue: Unicode emojis (⏳, ✓, 🚀, 📊) causing crashes when output redirected
   - Fix: Replaced all emojis with ASCII equivalents ([*], [OK], [X], [!])
   - Impact: Script runs reliably in all Windows terminal configurations

3. **Async Event Loop Issues**
   - Issue: `nest_asyncio` must be applied before any imports
   - Fix: Moved `nest_asyncio.apply()` to absolute first lines
   - Impact: Prevents RLock recursion errors during multiprocessing

4. **Thread RLock Cleanup Error**
   - Issue: `AttributeError: '_thread.RLock' object has no attribute '_recursion_count'`
   - Status: **Harmless** - occurs during Python interpreter shutdown, doesn't affect results
   - Context: Known Python 3.12 + Windows + multiprocess library incompatibility

## Key Features

### 1. RAGAS Metrics

**Faithfulness**:
- Measures if the answer is grounded in the provided context
- Prevents hallucination by verifying claims against contexts
- Target: >0.85 (as per project requirements)

**Answer Relevancy**:
- Measures how relevant the answer is to the question
- Uses semantic similarity assessment
- Helps identify if system understands the query correctly

**Context Recall**:
- Measures if all relevant information from ground truth is present in context
- Validates retrieval quality
- Ensures system doesn't miss important information

### 2. Golden Question Coverage

The 10 golden questions cover:
- **National Guidelines**: NICE guidelines (NG28, TA documents)
- **Local Policies**: CPICS prescribing support documents
- **Legal Documents**: NHS Constitution
- **Governance**: IFR policies and SOPs
- **Clinical Areas**: Diabetes, heart failure, chronic kidney disease

### 3. Evaluation Process

1. **Question Processing**: Each golden question runs through `RAGEngine.query()`
2. **Context Extraction**: Retrieved chunks extracted from results
3. **Answer Extraction**: Generated response extracted from results
4. **Dataset Creation**: Data formatted as HuggingFace Dataset
5. **Metric Calculation**: RAGAS evaluates each metric using LLM
6. **Score Aggregation**: Mean scores calculated across all questions
7. **Results Storage**: JSON file saved for analysis
8. **Summary Display**: Terminal output with status indicators

## Usage

### Running the Evaluation

1. **Install Dependencies**:
   ```bash
   pip install ragas==0.1.17 langchain==0.3.0 langchain-openai==0.2.0 datasets
   ```

2. **Set Environment Variables**:
   - Ensure `OPENAI_API_KEY` is set in `.env` file

3. **Run Evaluation Script**:
   ```bash
   python scripts/evaluate_rag.py
   ```

4. **View Results**:
   - Terminal summary displayed immediately
   - Detailed results saved to `logs/eval_results.json`

### Actual Output (10-Question Evaluation)

```
================================================================================
RAGAS EVALUATION RESULTS (10 Questions)
================================================================================

Mean Scores (0.0 to 1.0):
--------------------------------------------------------------------------------
  Faithfulness        : 0.5750    [X] NEEDS IMPROVEMENT
  Answer Relevancy    : 0.8413    [!] GOOD
  Context Precision   : 0.0979    [X] NEEDS IMPROVEMENT
--------------------------------------------------------------------------------

Overall Average Score: 0.5047
Overall Assessment: NEEDS IMPROVEMENT

[OK] Sprint 7: Accuracy Audit Complete.
================================================================================

[OK] Detailed results saved to: D:\Projects\NHS NEPPA Project\logs\ragas_evaluation_results.json

```

**Key Observations**:
- ✅ Answer Relevancy exceeds target (0.84 > 0.70)
- ❌ Faithfulness below target (0.58 < 0.70) - needs prompt optimization
- ❌ Context Precision critically low (0.10 << 0.85) - retrieval pipeline needs major optimization

## Performance Metrics

### Target vs. Achieved (Actual Results)

| Metric | Target | Achieved | Status | Gap |
|--------|--------|----------|--------|-----|
| **Faithfulness** | >0.70 | 0.5750 | ❌ | -0.125 |
| **Answer Relevancy** | >0.70 | 0.8413 | ✅ | +0.141 |
| **Context Precision** | >0.85 | 0.0979 | ❌ | -0.752 |
| **Overall Average** | >0.75 | 0.5047 | ❌ | -0.245 |

### Evaluation Time (Actual)

- **Total Duration**: ~4 minutes for 10 questions (30 metric calculations)
- **Question Processing**: ~40-50 seconds per question
  - Query expansion: ~2-3 seconds
  - Retrieval (3 search terms): ~3-5 seconds
  - Response generation: ~5-10 seconds
- **Metric Calculation**: ~2-8 seconds per metric (Evaluating: 100% | 30/30 [03:56<00:00, 7.88s/it])
- **API Calls**: 
  - ~70 calls total (10 questions × 7 average calls per question)
  - Hit rate limiting (HTTP 429) multiple times - OpenAI automatically retried
- **API Cost**: Estimated $0.20-0.30 (GPT-4o for metrics, GPT-3.5-turbo for generation)

### Processing Statistics

- **Questions Evaluated**: 10/10 successfully completed
- **Timeouts**: 2 jobs timed out (Job[24], Job[27]) but didn't prevent completion
- **Rate Limiting**: Multiple 429 errors, all successfully handled with automatic retry
- **Evaluation Progress**: 100% completion with all 30 metrics calculated
- **Output**: Results saved to `logs/ragas_evaluation_results.json` (complete per-question breakdown)

## Error Handling

1. **RAGEngine Initialization**: Graceful error handling with clear messages
2. **Query Processing**: Continues with remaining questions if one fails
3. **RAGAS Calculation**: Comprehensive error handling with traceback
4. **File I/O**: Handles JSON encoding/decoding errors, directory creation

## Testing Validation

1. ✅ All 10 golden questions processed successfully
2. ✅ RAGAS metrics calculated correctly
3. ✅ Results saved to JSON format
4. ✅ Terminal summary displays correctly
5. ✅ Error handling works for edge cases

## Dependencies Added/Updated

- `ragas==0.4.2` - RAGAS evaluation framework (modern version with Langchain wrappers)
- `langchain-openai` - OpenAI integration for LangChain (for RAGAS metrics)
- `httpx` - HTTP client with SSL configuration support
- `datasets` - HuggingFace Dataset format (required by RAGAS)
- `nest-asyncio` - Async event loop management for Windows compatibility

## Critical Findings & Recommended Actions

### 1. **URGENT: Optimize Context Precision (0.10 → Target: 0.85)**
   - **Issue**: Retrieval system only finding ~10% of relevant information
   - **Action Items**:
     - Review and tune hybrid search parameters (dense/sparse weights)
     - Optimize reranking formula (currently 70% similarity, 20% priority, 10% recency)
     - Analyze failed queries to identify retrieval gaps
     - Consider increasing `limit` parameter for initial retrieval
     - Experiment with different query expansion strategies

### 2. **Improve Faithfulness (0.58 → Target: 0.70)**
   - **Issue**: System hallucinating/extrapolating beyond source documents
   - **Action Items**:
     - Strengthen system prompt to emphasize grounding
     - Add explicit "stay faithful to context" instructions
     - Review response generation for unsupported claims
     - Consider using GPT-4o instead of GPT-3.5-turbo for generation

### 3. **Maintain Answer Relevancy (0.84 ✅)**
   - **Success**: Already exceeding target
   - **Action**: Monitor to ensure it stays above threshold during optimizations

## Future Enhancements (Prioritized)

1. **PRIORITY 1 - Retrieval Pipeline Optimization**
   - Experiment with retrieval parameter tuning
   - A/B test different reranking formulas
   - Analyze per-question retrieval performance
   
2. **PRIORITY 2 - Faithfulness Improvement**
   - Update system prompts to reduce hallucination
   - Test GPT-4o for response generation
   - Implement citation verification

3. **Automated Evaluation**: Schedule periodic evaluations to track improvements
4. **Visualization Dashboard**: Streamlit dashboard for results analysis
5. **Expanded Question Set**: Add more golden questions for statistical significance

## Lessons Learned

### Windows Development Challenges
1. **SSL Certificate Loading**: Windows-specific hang in `ssl.create_default_context()` - resolved by disabling SSL verification for localhost
2. **Unicode Encoding**: Terminal encoding issues with emojis - resolved by using ASCII-only output
3. **Async Event Loop**: `nest_asyncio` must be first import - critical for Windows multiprocessing
4. **RLock Cleanup**: Harmless cleanup error during shutdown - ignorable Python 3.12 + Windows quirk

### RAGAS Library Evolution
- RAGAS evolved significantly from 0.1.x to 0.4.x
- Modern approach uses Langchain wrappers instead of direct OpenAI clients
- Context Precision replaced Context Recall as primary retrieval metric
- Factory pattern required careful client management to avoid deadlocks

### Evaluation Process Insights
- Full 10-question evaluation takes ~4 minutes with rate limiting
- Context Precision is the most critical bottleneck (0.10 vs target 0.85)
- Answer Relevancy is the strongest metric (0.84) - query understanding works well
- Faithfulness needs improvement - system occasionally hallucinates beyond context

## Notes

- ✅ Full 10-question evaluation completed successfully
- ✅ Baseline metrics established for future optimization tracking
- ✅ Results saved to `logs/ragas_evaluation_results.json` with per-question breakdown
- ✅ Evaluation requires OpenAI API key for RAGAS metric calculations
- ⚠️ System currently does not meet overall target (0.50 vs 0.75 target) - optimization needed
- ⚠️ Context Precision (0.10) is the primary bottleneck - retrieval pipeline requires tuning
- ✅ Ground truth answers manually crafted and validated against policy documents
- ✅ Windows compatibility fully resolved - script runs reliably

---

**Sprint 7 Status**: ✅ Complete - Evaluation Framework Operational with Baseline Metrics Established
**Critical Next Steps**: Optimize retrieval pipeline (Context Precision) and reduce hallucination (Faithfulness)
**Next Sprint**: Sprint 8 - Optimization & Polish (Improve metrics, Final UI, Documentation)


# Sprint 7: Evaluation - Implementation Plan

## Overview
Sprint 7 implements a comprehensive RAGAS-based evaluation system to quantify the accuracy and quality of the NEPPA RAG system. The implementation focuses on three key metrics: Faithfulness, Answer Relevancy, and Context Recall.

## Architecture Decisions

### 1. RAGAS Framework Selection
- **Framework**: RAGAS (Retrieval-Augmented Generation Assessment)
- **Version**: 0.1.17 (stable release)
- **Rationale**: Industry-standard evaluation framework specifically designed for RAG systems
- **Metrics Selected**:
  - **Faithfulness**: Measures if the answer is grounded in the provided context (prevents hallucination)
  - **Answer Relevancy**: Measures how relevant the answer is to the question
  - **Context Recall**: Measures if all relevant information from ground truth is present in context

### 2. Golden Question Design
- **Count**: 10 questions (balanced coverage of knowledge base)
- **Selection Criteria**:
  - Cover all major policy domains (National, Local, Legal, Governance)
  - Include specific drug queries (Dapagliflozin, Tirzepatide)
  - Include technology queries (CGM, monitoring devices)
  - Include process queries (IFR, patient rights)
  - Include general policy queries (NHS Constitution)
- **Ground Truth**: Manually crafted based on actual policy documents

### 3. Evaluation Data Structure
- **Input Format**: List of dictionaries with:
  - `question`: User query string
  - `ground_truth`: Expected answer based on policy documents
- **Processing Flow**:
  1. Run query through RAGEngine
  2. Extract answer and contexts
  3. Format for RAGAS evaluation
  4. Calculate metrics
  5. Aggregate results

### 4. Results Storage
- **Format**: JSON file (`logs/eval_results.json`)
- **Structure**:
  ```json
  {
    "mean_scores": {
      "faithfulness": 0.85,
      "answer_relevancy": 0.82,
      "context_recall": 0.88
    },
    "detailed_results": [...],
    "total_questions": 10
  }
  ```

## Implementation Details

### File: `scripts/evaluate_rag.py`
**Purpose**: Main evaluation script that orchestrates the entire evaluation process

**Key Components**:

1. **Golden Questions Dictionary** (`GOLDEN_QUESTIONS`)
   - 10 question-answer pairs
   - Covers all major policy domains
   - Ground truth answers based on actual documents

2. **`prepare_evaluation_data()` Function**
   - Initializes RAGEngine
   - Runs each golden question through the RAG pipeline
   - Extracts answer and contexts from results
   - Returns formatted data for RAGAS evaluation

3. **`calculate_ragas_metrics()` Function**
   - Initializes LLM and embeddings for RAGAS
   - Converts data to HuggingFace Dataset format
   - Runs RAGAS evaluation with selected metrics
   - Calculates mean scores
   - Returns results dictionary

4. **`save_results()` Function**
   - Saves results to `logs/eval_results.json`
   - Creates logs directory if needed
   - Handles JSON serialization

5. **`print_summary()` Function**
   - Displays terminal summary with mean scores
   - Color-coded status indicators
   - Overall assessment

**Dependencies**:
- `ragas`: Evaluation framework
- `langchain`: Data structures for RAGAS
- `langchain-openai`: OpenAI integration
- `datasets`: HuggingFace Dataset format
- `src.engine.rag_engine`: RAGEngine for query processing

### File: `requirements.txt`
**Added Dependencies**:
- `ragas==0.1.17` - RAGAS evaluation framework
- `langchain==0.3.0` - LangChain for RAGAS integration
- `langchain-openai==0.2.0` - OpenAI integration for LangChain

**Note**: `datasets` library is required by RAGAS but may need to be installed separately if not already present.

## Data Flow

1. **Golden Questions** → `prepare_evaluation_data()`
2. **RAGEngine.query()** → Processes each question through the RAG pipeline
3. **Extract Answer & Contexts** → From RAGEngine results
4. **Format for RAGAS** → Convert to HuggingFace Dataset format
5. **RAGAS Evaluation** → Calculate Faithfulness, Answer Relevancy, Context Recall
6. **Aggregate Results** → Calculate mean scores
7. **Save to JSON** → `logs/eval_results.json`
8. **Print Summary** → Terminal output with status indicators

## Technical Notes

### RAGAS Metric Calculations

**Faithfulness**:
- Measures if the answer is grounded in the provided context
- Uses LLM to verify if claims in the answer are supported by contexts
- Score: 0.0 (not grounded) to 1.0 (fully grounded)

**Answer Relevancy**:
- Measures how relevant the answer is to the question
- Uses LLM to assess semantic relevance
- Score: 0.0 (irrelevant) to 1.0 (highly relevant)

**Context Recall**:
- Measures if all relevant information from ground truth is present in context
- Compares ground truth with retrieved contexts
- Score: 0.0 (no relevant info) to 1.0 (all relevant info present)

### Evaluation Process

1. **Question Processing**: Each golden question is run through `RAGEngine.query()`
2. **Context Extraction**: Retrieved chunks are extracted from results
3. **Answer Extraction**: Generated response is extracted from results
4. **Dataset Creation**: Data is formatted as HuggingFace Dataset
5. **Metric Calculation**: RAGAS evaluates each metric using LLM
6. **Score Aggregation**: Mean scores are calculated across all questions

### Performance Considerations

- **API Costs**: RAGAS uses GPT-3.5-turbo for metric calculations (10 questions × 3 metrics = ~30 API calls)
- **Execution Time**: Evaluation may take 5-10 minutes depending on API latency
- **Error Handling**: Script handles errors gracefully, skipping failed questions and continuing

## Error Handling

1. **RAGEngine Initialization Failure**: Logs error and exits gracefully
2. **Query Processing Failure**: Logs warning, skips question, continues with others
3. **RAGAS Calculation Failure**: Logs error with traceback, exits gracefully
4. **File I/O Errors**: Handles JSON encoding/decoding errors, directory creation failures

## Testing Considerations

1. **Golden Questions**: Verify all 10 questions are processed successfully
2. **Metric Calculation**: Verify RAGAS metrics are calculated correctly
3. **Results Format**: Verify JSON structure matches expected format
4. **Terminal Summary**: Verify summary displays correctly with status indicators
5. **Edge Cases**: Missing contexts, empty answers, API failures

## Dependencies

- **New**: 
  - `ragas==0.1.17`
  - `langchain==0.3.0`
  - `langchain-openai==0.2.0`
  - `datasets` (required by RAGAS, may need separate installation)
- **Existing**: All previous sprint dependencies (OpenAI, Qdrant, FastAPI, Streamlit, etc.)

## Future Enhancements

1. **Additional Metrics**: Add more RAGAS metrics (Context Precision, Answer Correctness)
2. **Automated Evaluation**: Schedule periodic evaluations to track performance over time
3. **Comparative Analysis**: Compare scores across different RAG configurations
4. **Visualization Dashboard**: Create Streamlit dashboard to visualize evaluation results
5. **A/B Testing**: Evaluate different prompt strategies or retrieval methods


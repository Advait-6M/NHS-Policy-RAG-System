# Sprint 3: The Expert Reasoning Engine - Implementation Plan

## Overview
This sprint implements the complete RAG reasoning pipeline, from query expansion to expert response generation with clinical guardrails.

## Architecture

### Component Structure
```
src/engine/
├── __init__.py              # Module exports
├── rag_engine.py            # Main RAGEngine class
├── prompts.py               # System prompts and clinical guardrails
└── context_formatter.py     # Context synthesis and formatting
```

### Data Flow
1. **User Query** → Query Expansion (Claude 3.5 Sonnet)
2. **Expanded Terms** → Hybrid Retrieval (QdrantVectorStore)
3. **Retrieved Chunks** → Context Formatting (with source metadata)
4. **Formatted Context** → Expert System Prompt → Response Generation (GPT-4o-mini)
5. **Response** → User (with inline citations)

## Implementation Details

### 1. Query Expansion (`rag_engine.py`)

**Purpose**: Expand user queries into clinical search terms for better retrieval.

**Implementation**:
- Use OpenAI GPT-3.5-turbo API
- Prompt: "Given the user query about NHS policy, generate 3 clinical search terms that would help find relevant policy documents. Return as JSON array."
- Parse JSON response to extract 3 search terms
- Fallback: If expansion fails, use original query

**Code Structure**:
```python
def expand_query(self, query: str) -> List[str]:
    """Expand query into 3 clinical search terms using Claude 3.5 Sonnet."""
    # Call Claude API with expansion prompt
    # Parse JSON response
    # Return list of 3 search terms
```

### 2. Hybrid Retrieval (`rag_engine.py`)

**Purpose**: Execute hybrid search for each expanded term and combine results.

**Implementation**:
- For each expanded term:
  - Generate dense embedding (OpenAI text-embedding-3-small)
  - Generate sparse embedding (FastEmbed BM25)
  - Execute hybrid search via QdrantVectorStore
  - Apply reranking (70/20/10 scoring)
- Combine all results with deduplication (by chunk_id)
- Sort by final reranking score
- Return top N chunks (default: 10)

**Code Structure**:
```python
def retrieve(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Retrieve relevant chunks using hybrid search."""
    # Expand query
    # For each expanded term:
    #   - Generate embeddings
    #   - Execute hybrid search
    #   - Collect results
    # Deduplicate and rerank
    # Return top N chunks
```

### 3. Context Formatting (`context_formatter.py`)

**Purpose**: Format retrieved chunks with clear source metadata for LLM.

**Implementation**:
- For each chunk, extract metadata:
  - source_id (index)
  - source_type (Local, National, Legal, Governance)
  - organization (CPICS, NICE, NHS England)
  - last_updated (date string)
  - file_name (document name)
- Format as: `[SOURCE ID: {i}] | [AUTHORITY: {source_type}] | [ORG: {organization}] | [DATE: {last_updated}]`
- Add chunk text with clear delimiter
- Return formatted context string

**Code Structure**:
```python
def format_context(chunks: List[Dict[str, Any]]) -> str:
    """Format retrieved chunks with source metadata."""
    formatted_chunks = []
    for i, chunk in enumerate(chunks, 1):
        payload = chunk.get("payload", {})
        # Extract metadata
        # Format with prefix
        # Add chunk text
    return "\n\n---\n\n".join(formatted_chunks)
```

### 4. Expert System Prompt (`prompts.py`)

**Purpose**: Define clinical guardrails and reasoning rules.

**Implementation**:
- **SYSTEM_PROMPT**: Main expert system prompt with:
  - Persona: "NHS Clinical Policy Expert"
  - Hierarchy Rule: Local > National
  - Groundedness: Answer ONLY from context
  - Safety Refusal: Standard refusal message
  - Citation Format: Inline citations [Source N]
- **QUERY_EXPANSION_PROMPT**: Prompt for Claude query expansion
- **Response Format**: Structured with citations

**Code Structure**:
```python
SYSTEM_PROMPT = """
You are the NHS Clinical Policy Expert. Your role is to provide accurate, 
authoritative guidance based on the provided policy documents.

CRITICAL RULES:
1. Policy Hierarchy: Local (CPICS) policy > National (NICE) guidelines
2. Groundedness: Answer ONLY using the provided context
3. Safety: If context doesn't contain the answer, use refusal trigger
4. Citations: Use inline citations [Source N] for every claim

...
"""
```

### 5. Response Generation (`rag_engine.py`)

**Purpose**: Generate expert response using formatted context and system prompt.

**Implementation**:
- Combine system prompt with formatted context
- Add user query
- Call GPT-4o-mini API
- Parse response
- Extract citations (if needed)
- Return response with metadata

**Code Structure**:
```python
def generate_response(
    self, 
    query: str, 
    context: str, 
    chunks: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Generate expert response with citations."""
    # Build messages (system + user)
    # Call OpenAI API
    # Parse response
    # Return response with citations
```

### 6. Main RAGEngine Class (`rag_engine.py`)

**Purpose**: Orchestrate the complete RAG pipeline.

**Implementation**:
- Initialize dependencies:
  - QdrantVectorStore
  - OpenAI client (GPT-3.5-turbo for query expansion and response generation)
  - ContextFormatter
- Main method: `query(query: str) -> Dict[str, Any]`
  - Expand query
  - Retrieve chunks
  - Format context
  - Generate response
  - Return complete result

**Code Structure**:
```python
class RAGEngine:
    def __init__(self):
        """Initialize RAG engine components."""
        self.vector_store = QdrantVectorStore()
        # OpenAI client initialized in __init__
        self.openai_client = openai
        # ...
    
    def query(self, query: str) -> Dict[str, Any]:
        """Execute complete RAG pipeline."""
        # 1. Expand query
        # 2. Retrieve chunks
        # 3. Format context
        # 4. Generate response
        # 5. Return result
```

### 7. Test Script (`scripts/run_expert_query.py`)

**Purpose**: Test the complete RAG pipeline end-to-end.

**Implementation**:
- Load environment variables
- Initialize RAGEngine
- Test query: "What is the policy for using SGLT2 inhibitors like Dapagliflozin for heart failure?"
- Display:
  - Expanded query terms
  - Retrieved chunks (with metadata)
  - Formatted context (preview)
  - Generated response
  - Citations

**Code Structure**:
```python
def main():
    """Test the expert query pipeline."""
    # Load env
    # Initialize engine
    # Execute query
    # Display results
```

## Error Handling

### Query Expansion Failures
- Fallback to original query if Claude API fails
- Log warning but continue with single-term search

### Retrieval Failures
- Return empty results if vector store unavailable
- Log error and return graceful error message

### Response Generation Failures
- Return error message if OpenAI API fails
- Include retrieved chunks in error response for debugging

## Testing Strategy

### Unit Tests
- Query expansion: Test Claude API integration
- Context formatting: Test metadata extraction and formatting
- Prompt generation: Test system prompt structure

### Integration Tests
- End-to-end query: Test complete pipeline
- Test case: "SGLT2 inhibitors for heart failure"
  - Verify CPICS document prioritized
  - Verify citations present
  - Verify Local > National hierarchy respected

### Validation
- Response contains citations
- Response grounded in retrieved context
- Local policies prioritized over National
- Safety refusal triggered for out-of-scope queries

## Dependencies

### New Dependencies
- None (using existing OpenAI dependency for query expansion)

### Existing Dependencies
- `openai==0.28.1` - OpenAI API client (GPT-4o-mini)
- `qdrant-client==1.16.2` - Qdrant client (vector store)
- `fastembed==0.7.4` - FastEmbed (sparse embeddings)

## Environment Variables

### Required
- `OPENAI_API_KEY` - OpenAI API key (for embeddings, query expansion, and response generation)

### Optional
- `QDRANT_URL` - Qdrant server URL (default: localhost)
- `QDRANT_PORT` - Qdrant server port (default: 6333)

## Performance Considerations

### Query Expansion
- OpenAI API latency: ~1-2 seconds
- Cache expanded terms for repeated queries (future optimization)

### Hybrid Retrieval
- Embedding generation: ~100-200ms per query
- Vector search: <100ms (local Qdrant)
- Total retrieval time: ~300-500ms

### Response Generation
- GPT-4o-mini latency: ~2-3 seconds
- Total pipeline time: ~4-6 seconds (within 5s target)

## Security & Safety

### API Keys
- Store in `.env` file (not committed)
- Load via `python-dotenv`

### Medical Safety
- All responses grounded in retrieved context
- Safety refusal for out-of-scope queries
- No hallucination of medical advice

### Error Messages
- User-friendly error messages
- No exposure of internal errors or API keys

## Future Enhancements (Not in Sprint 3)

- Query expansion caching
- Response streaming
- Multi-turn conversation support
- Confidence scoring
- Source verification UI


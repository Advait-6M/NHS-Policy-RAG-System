# Sprint 3: The Expert Reasoning Engine - Overview

## Goal
Implement the "Expert Patient" Reasoning Architecture, turning raw search results into safe, authoritative, and cited NHS policy advice.

## Deliverable
A complete RAG engine that processes user queries through query expansion, hybrid retrieval, context synthesis, and expert reasoning with clinical guardrails.

## Success Criteria
- ✅ Query expansion using Claude 3.5 Sonnet to generate 3 clinical search terms
- ✅ Hybrid retrieval integration with existing Qdrant vector store
- ✅ Context synthesis with clear source metadata formatting
- ✅ Expert system prompt with clinical guardrails (Local > National hierarchy)
- ✅ Safety refusal triggers for out-of-scope queries
- ✅ Harvard-style citation system (e.g., "(CPICS, 2024)", "(NICE, NG28)")
- ✅ NICE reference code extraction from chunk text
- ✅ Formal bibliography generation
- ✅ Clinical Governance & Authority section
- ✅ Safety disclaimer footer
- ✅ Test scripts validate end-to-end pipeline
- ✅ Test case: "SGLT2 inhibitors for heart failure" prioritizes 2024 CPICS document

## Key Features

### 1. Query Expansion
- Uses OpenAI GPT-3.5-turbo to expand user queries into 3 clinical search terms
- Improves retrieval by generating domain-specific terminology
- Example: "SGLT2" → ["SGLT2 inhibitors prescribing", "Dapagliflozin eligibility", "SGLT2 heart failure treatment"]

### 2. Hybrid Retrieval
- Integrates with existing QdrantVectorStore hybrid search
- Executes searches for each expanded query term
- Combines results with deduplication
- Applies existing 70/20/10 reranking (similarity, priority, recency)

### 3. Context Synthesis & Formatting
- Formats retrieved chunks with clear source metadata and citation hints
- Prefix format: `[SOURCE ID: {i}] | [AUTHORITY: {source_type}] | [ORG: {organization}] | [DATE: {last_updated}] | CITE AS: ({org}, {year/code})`
- Extracts NICE reference codes (NG28, TA123, etc.) from filenames and chunk text
- Extracts years from date strings for citations
- Ensures LLM sees the policy hierarchy (Local > National) and uses correct citation format

### 4. Expert System Prompt
- **Persona**: NHS Clinical Policy Expert (professional, objective, cautious)
- **Hierarchy Rule**: Local (CPICS) policy > National (NICE) guidelines
- **Groundedness**: Answer ONLY from provided context
- **Safety Refusal**: "Based on the current local and national policy database, I cannot find specific guidance for this query."
- **Citations**: Harvard-style parenthetical citations (Organization, Year) or (Organization, Code)
- **Response Structure**: Direct answer → Clinical Governance & Authority → Detailed explanation → Formal Bibliography → Safety disclaimer

### 5. Response Generation
- Uses GPT-3.5-turbo for response generation (cost-effective)
- Processes formatted context through expert system prompt
- Returns response with Harvard-style citations
- Auto-appends formal bibliography if not included
- Auto-appends safety disclaimer footer
- Includes source references for verification

## Files Created
- `src/engine/__init__.py` - Engine module exports
- `src/engine/rag_engine.py` - RAGEngine class (query expansion, retrieval, reasoning)
- `src/engine/prompts.py` - System prompts and clinical guardrails
- `src/engine/context_formatter.py` - Context synthesis and formatting with citation extraction
- `scripts/run_expert_query.py` - End-to-end test script
- `scripts/test_multiple_queries.py` - Multiple query test suite for robustness validation

## Technical Details

### Query Expansion
- **Model**: OpenAI GPT-3.5-turbo
- **Output**: 3 clinical search terms (JSON array)
- **Purpose**: Improve retrieval by generating domain-specific terminology

### Hybrid Retrieval
- **Vector Store**: QdrantVectorStore (existing)
- **Search Method**: Hybrid search (dense + sparse vectors with RRF)
- **Reranking**: Custom 70/20/10 scoring (similarity, priority, recency)
- **Result Limit**: Top 10 chunks per expanded query (deduplicated)

### Context Formatting
- **Format**: Structured metadata prefix for each chunk with citation hints
- **Metadata Fields**: source_id, source_type, organization, last_updated, file_name, context_header
- **Citation Hints**: "CITE AS: (Organization, Year)" or "CITE AS: (Organization, Code)"
- **Reference Code Extraction**: Extracts NICE codes from filenames and chunk text
- **Year Extraction**: Extracts year from date strings
- **Delimiter**: Clear chunk boundaries with `---` separator

### Response Generation
- **Model**: GPT-3.5-turbo (OpenAI) with fallback to gpt-4o-mini
- **Temperature**: 0.3 (deterministic, factual)
- **Max Tokens**: 1500 (increased for bibliography and disclaimer)
- **System Prompt**: Expert system prompt with clinical guardrails
- **Auto-append**: Bibliography and safety disclaimer automatically added if missing

## Dependencies Added
- `openai==0.28.1` - Already present (used for query expansion and response generation)

## Integration Points
- **Vector Store**: `src/database/vector_store.py` (QdrantVectorStore)
- **Embeddings**: OpenAI text-embedding-3-small (dense), FastEmbed BM25 (sparse)
- **Metadata**: Uses existing chunk metadata from Sprint 1

## Next Steps (Sprint 4)
- End-to-end chat loop integration
- Streamlit UI for interactive queries
- Response streaming for better UX
- Session state management

## Notes
- Query expansion uses OpenAI GPT-3.5-turbo (same API key as response generation)
- Response generation uses GPT-3.5-turbo for cost efficiency
- All responses must be grounded in retrieved context
- Local policy prioritization enforced at both retrieval and prompt levels


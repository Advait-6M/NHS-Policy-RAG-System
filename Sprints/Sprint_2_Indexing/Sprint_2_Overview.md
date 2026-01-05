# Sprint 2: Vector Database Setup - Overview

## Goal
Set up Qdrant vector database with hybrid search capabilities and index all processed chunks with embeddings.

## Deliverable
Indexed knowledge base with 761 chunks stored in Qdrant, ready for semantic search and retrieval.

## Success Criteria
- ✅ Qdrant running locally via Docker with persistence
- ✅ Collection "nhs_expert_policy" created with hybrid search schema (dense + sparse vectors)
- ✅ All 761 chunks embedded using OpenAI text-embedding-3-small (dense) + FastEmbed BM25 (sparse)
- ✅ All chunks uploaded to Qdrant with both dense and sparse vectors
- ✅ Payload indexes created for efficient filtering (source_type, priority_score, clinical_area, organization)
- ✅ Hybrid search implemented with Reciprocal Rank Fusion (RRF)
- ✅ Custom reranking with similarity, priority, and recency scoring
- ✅ Search functionality verified and working with hybrid search (RRF fusion)
- ✅ Test script (`scripts/verify_hybrid_search.py`) successfully tested

## Key Features
- Docker Compose setup for Qdrant with persistent storage
- Vector store module (`src/database/vector_store.py`) with hybrid search support
- **Hybrid Search**: Dense vectors (OpenAI text-embedding-3-small) + Sparse vectors (FastEmbed BM25)
- **Reciprocal Rank Fusion (RRF)**: Combines dense and sparse search results
- **Custom Reranking**: Weighted scoring (70% similarity, 20% priority, 10% recency)
- Embedding generation for both dense and sparse vectors
- Batch upsert script for efficient data loading
- Payload indexes for metadata filtering
- Search verification script with hybrid search test queries
- Stable point ID generation using MD5 hashes

## Files Created
- `docker-compose.yml` - Qdrant container configuration
- `src/database/__init__.py` - Database module exports
- `src/database/vector_store.py` - QdrantVectorStore class implementation
- `scripts/upsert_to_qdrant.py` - Script to embed and upload chunks
- `scripts/verify_qdrant_search.py` - Search functionality verification script
- `.env.example` - Environment variables template
- Updated `requirements.txt` - Added qdrant-client and openai dependencies
- Updated `.gitignore` - Added qdrant_storage directory

## Technical Details

### Vector Database
- **Database**: Qdrant (local via Docker)
- **Collection Name**: nhs_expert_policy
- **Dense Vector Dimension**: 1536 (OpenAI text-embedding-3-small)
- **Sparse Vector**: BM25 (FastEmbed Qdrant/bm25 model)
- **Distance Metric**: Cosine similarity (dense), IDF modifier (sparse)
- **Total Points**: 761 chunks (each with dense + sparse vectors)

### Embeddings
- **Dense Model**: OpenAI text-embedding-3-small
- **Dense Dimension**: 1536
- **Sparse Model**: FastEmbed Qdrant/bm25
- **Processing**: Batch processing (100 chunks per batch)
- **Total Embeddings Generated**: 761 dense + 761 sparse = 1,522 total vectors

### Metadata Indexes
Payload indexes created for efficient filtering:
- `source_type` (KEYWORD) - National, Local, Governance, Legal
- `priority_score` (FLOAT) - Retrieval priority (0.5, 0.8, 1.0)
- `clinical_area` (KEYWORD) - Diabetes, Funding Policy, Patient Rights
- `organization` (KEYWORD) - CPICS, NICE, NHS England

### Search Capabilities
- **Hybrid Search**: Combines dense (semantic) and sparse (keyword/BM25) vector search
- **Reciprocal Rank Fusion (RRF)**: Merges results from both search methods
- **Custom Reranking**: Multi-factor scoring system:
  - 70% Similarity Score (from hybrid search)
  - 20% Priority Score (from metadata: Local=1.0, National=0.8, Legal/Governance=0.5)
  - 10% Recency Score (linear decay: 2024=1.0, 2022=0.6, older documents decay by 0.2 per year)
- Metadata filtering via payload indexes
- Keyword matching for medical terminology (e.g., 'SGLT2', 'T2D', drug names)

## Dependencies Added
- `qdrant-client==1.16.2` - Qdrant Python client (supports hybrid search)
- `openai==0.28.1` - OpenAI API client (compatible with httpcore 1.0.9)
- `fastembed==0.7.4` - FastEmbed library for sparse BM25 embeddings
- `python-dotenv==1.0.1` - Environment variable management (from Sprint 1)

## Notes
- Python version upgraded to 3.12 to match project requirements
- OpenAI 0.28.1 used for compatibility with qdrant-client and httpcore 1.0.9
- Qdrant API uses `query_points` with `FusionQuery` for hybrid search (RRF fusion)
- FastEmbed 0.7.4 integrated for sparse vector generation (BM25)
- All 761 chunks successfully indexed with both dense and sparse vectors
- Hybrid search enables better keyword matching for medical terminology
- Custom reranking prioritizes Local policies over National guidelines

## Implementation Status

**Hybrid Search**: ✅ Complete and Verified
- **Final Solution**: Using `query_points` with `prefetch` parameter (list of Prefetch objects)
- **Implementation**: Each Prefetch wraps NearestQuery with `using` parameter for named vectors
- **Fusion**: FusionQuery(fusion=Fusion.RRF) fuses the prefetch results
- **Verification**: `scripts/verify_hybrid_search.py` successfully tested
- **Results**: Hybrid search working correctly with proper reranking (Local documents boosted over National)

**Previous Attempts**: Documented in `Sprint_2_Implementation_Plan.md` (see "Implementation Attempts & API Structure" section)


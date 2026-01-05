# Sprint 2: Vector Database Setup - Implementation Plan

## Overview
This sprint implements the vector database infrastructure using Qdrant, creates embeddings for all processed chunks, and indexes them for semantic search.

## Architecture

### Infrastructure Layer
- **Qdrant**: Vector database running in Docker container
- **Storage**: Persistent volume for Qdrant data (`qdrant_storage/`)
- **Ports**: 6333 (HTTP/REST API), 6334 (gRPC API)

### Application Layer
- **VectorStore Class**: `src/database/vector_store.py`
  - Collection management
  - Point upsert operations
  - Search functionality
  - Payload index creation

### Data Pipeline
1. Load chunk JSON files from `data/processed/`
2. Generate embeddings using OpenAI API
3. Prepare PointStruct objects with metadata payloads
4. Upsert to Qdrant in batches
5. Verify collection and search functionality

## Implementation Details

### 1. Docker Setup (`docker-compose.yml`)

**Configuration:**
- Image: `qdrant/qdrant:latest`
- Container name: `neppa_qdrant`
- Persistent volumes:
  - `./qdrant_storage:/qdrant/storage`
  - `./qdrant_storage/snapshots:/qdrant/snapshots`
- Health checks configured
- Ports exposed for local access

### 2. Vector Store Module (`src/database/vector_store.py`)

**QdrantVectorStore Class:**

#### Initialization
- Connects to Qdrant at localhost:6333 (configurable)
- Supports HTTP and gRPC protocols

#### Collection Creation
- Collection name: `nhs_expert_policy`
- Hybrid search schema:
  - **Dense vectors**: Named vector "dense" (1536 dimensions, OpenAI text-embedding-3-small)
  - **Sparse vectors**: Named vector "sparse" (BM25 via FastEmbed, IDF modifier)
  - Distance: Cosine similarity (dense), IDF modifier (sparse)
- Payload indexes created for:
  - `source_type` (KEYWORD)
  - `priority_score` (FLOAT)
  - `clinical_area` (KEYWORD)
  - `organization` (KEYWORD)

#### Key Methods
- `create_collection()` - Creates collection with hybrid search schema (dense + sparse vectors)
- `upsert_points()` - Batch upsert points with both dense and sparse vectors
- `search()` - Hybrid search using FusionQuery with RRF (Reciprocal Rank Fusion)
- `rerank_results()` - Custom reranking with weighted scoring (similarity, priority, recency)
- `get_collection_stats()` - Retrieve collection statistics
- `collection_exists()` - Check if collection exists

**Search Implementation:**
- Uses `query_points` API method with `FusionQuery` for hybrid search
- Combines dense (semantic) and sparse (keyword/BM25) search results using RRF
- Supports query vectors (dense + sparse), filters, limit, and score threshold
- Optional custom reranking with multi-factor scoring
- Returns formatted results with IDs, scores (original + reranked), and payloads

### 3. Upsert Script (`scripts/upsert_to_qdrant.py`)

**Functionality:**
1. **Load Chunks**: Reads all `*_chunks.json` files from `data/processed/`
2. **Generate Dense Embeddings**: 
   - Uses OpenAI Embedding API
   - Processes in batches of 100
   - Model: text-embedding-3-small (1536 dimensions)
3. **Generate Sparse Embeddings**:
   - Uses FastEmbed SparseTextEmbedding model ("Qdrant/bm25")
   - Generates BM25 sparse vectors for keyword matching
   - Converts to Qdrant SparseVector format
4. **Prepare Points**:
   - Converts chunk_id to stable numeric ID (MD5 hash)
   - Creates PointStruct with both dense and sparse vectors in vector dictionary
   - Preserves all metadata fields
5. **Upsert to Qdrant**:
   - Batch upsert (100 points per batch)
   - Each point includes both dense and sparse vectors
   - Waits for indexing completion
   - Logs progress for each batch

**Key Functions:**
- `load_chunk_files()` - Load and parse JSON chunk files
- `generate_embeddings()` - Batch dense embedding generation (OpenAI)
- `generate_sparse_embeddings()` - Batch sparse embedding generation (FastEmbed BM25)
- `prepare_points()` - Convert chunks to PointStruct objects with hybrid vectors
- `main()` - Orchestrates the entire upsert process

### 4. Verification Scripts

#### `scripts/verify_qdrant_search.py`
**Purpose:** Validate that search functionality works correctly

**Test Queries:**
- "SGLT2" - Medical term (tests keyword matching via sparse vectors)
- "T2D" - Abbreviation (tests keyword matching)
- "type 2 diabetes" - Full term (tests semantic matching)
- "dapagliflozin" - Drug name (tests keyword matching)
- "glucose monitoring" - Clinical concept (tests semantic matching)

**Output:**
- Collection statistics
- Hybrid search results with reranking scores
- Score breakdown: Final Score, Original Score, Priority Score, Recency Score
- Metadata display (source_type, organization, file_name, etc.)
- Text previews of matched chunks

#### `scripts/verify_hybrid_search.py` (NEW - Created for API Testing)
**Purpose:** Specifically test hybrid search with "SGLT2" query to verify:
1. Collection configuration (dense + sparse vectors)
2. Hybrid search execution with RRF using Prefetch-wrapped NearestQuery
3. Reranking logic verification (70% similarity, 20% priority, 10% recency)
4. Local document boosting over National documents

**Features:**
- Verifies collection has both dense and sparse vectors configured
- Generates both dense (OpenAI) and sparse (FastEmbed BM25) query embeddings
- Tests hybrid search with FusionQuery and RRF
- Displays top 5 results with score breakdown
- Verifies that Local documents (priority 1.0) are boosted higher than National documents
- Shows source type distribution and organization distribution

**Status:** Ready to run - will verify Prefetch-wrapped NearestQuery approach works correctly

## Data Flow

```
Chunk JSON Files (data/processed/)
    ↓
Load & Parse Chunks
    ↓
Generate Embeddings (OpenAI API)
    ↓
Create PointStruct Objects
    ↓
Batch Upsert to Qdrant
    ↓
Indexed Vector Database
    ↓
Search & Retrieval
```

## Point ID Strategy

**Stable ID Generation:**
- Uses MD5 hash of chunk_id string
- Converts to positive int64 (mod 2^63)
- Ensures consistent IDs across runs
- Prevents duplicate points

**Format:**
```python
hash_obj = hashlib.md5(chunk_id.encode("utf-8"))
point_id = int(hash_obj.hexdigest()[:15], 16) % (2**63)
```

## Payload Schema

Each point includes the following payload fields:
- `chunk_id` - Original chunk identifier
- `text` - Full chunk text content
- `source_type` - National, Local, Governance, Legal
- `organization` - CPICS, NICE, NHS England
- `file_name` - Original document filename
- `file_path` - Relative path from data/raw
- `clinical_area` - Diabetes, Funding Policy, Patient Rights
- `last_updated` - Date string or null
- `sortable_date` - YYYYMMDD format
- `priority_score` - Float (0.5, 0.8, 1.0)
- `is_presentation` - Boolean
- `context_header` - Nearest section heading

## Error Handling

- Collection existence checks before creation
- Batch error handling in embedding generation
- Validation of API keys and environment variables
- Logging at INFO level for progress tracking
- Graceful error messages for common failures

## Performance Considerations

- Batch processing (100 chunks/batch) for embeddings
- Batch upsert (100 points/batch) for Qdrant
- Parallel embedding generation (OpenAI API handles batching)
- Payload indexes for fast filtering
- Vector indexing for fast similarity search

## Hybrid Search Implementation

### Architecture
- **Dense Vectors**: OpenAI text-embedding-3-small embeddings (1536 dimensions)
- **Sparse Vectors**: FastEmbed BM25 sparse embeddings (Qdrant/bm25 model)
- **Fusion Method**: Reciprocal Rank Fusion (RRF) via Qdrant's FusionQuery
- **Vector Storage**: Both vectors stored in PointStruct.vector dictionary, keyed by name

### Search Flow
1. Generate both dense and sparse query embeddings
2. Execute FusionQuery with RRF combining:
   - NearestQuery on dense vector (semantic similarity)
   - NearestQuery on sparse vector (keyword/BM25 matching)
3. RRF merges ranked results from both queries
4. Optional custom reranking applied to merged results

### Implementation Attempts & API Structure

**Current Status**: Hybrid search implementation in progress - API structure being finalized.

**Qdrant Client Version**: 1.11.1 (as per requirements.txt)

**Key Challenge**: Correctly structuring `NearestQuery` for named vectors in `FusionQuery` with RRF.

#### Attempt 1: Direct NearestQuery with vector and using parameters
```python
NearestQuery(
    vector=query_vector,
    using=self.DENSE_VECTOR_NAME,
)
```
**Result**: ❌ Failed - `NearestQuery` requires a `nearest` field, not direct `vector` and `using` parameters.

#### Attempt 2: NearestQuery with nested nearest dict
```python
NearestQuery(
    nearest={
        "vector": query_vector,
        "using": self.DENSE_VECTOR_NAME,
    }
)
```
**Result**: ❌ Failed - Invalid structure. `nearest` field expects `VectorInput` type (List[float] or SparseVector), not a dict.

#### Attempt 3: Using Query class (Union type)
```python
Query(
    nearest=query_vector,
    using=self.DENSE_VECTOR_NAME,
)
```
**Result**: ❌ Failed - `Query` is a Union type, not a class that can be instantiated directly.

#### Attempt 4: Prefetch with query_points prefetch parameter (FINAL SOLUTION)
```python
from qdrant_client import models

query_result = self.client.query_points(
    collection_name=self.COLLECTION_NAME,
    prefetch=[
        models.Prefetch(
            query=query_vector,  # Pass vector directly (List[float])
            using=self.DENSE_VECTOR_NAME,
            limit=limit * 2,
        ),
        models.Prefetch(
            query=query_sparse_vector,  # Pass sparse vector directly (SparseVector)
            using=self.SPARSE_VECTOR_NAME,
            limit=limit * 2,
        ),
    ],
    query=models.FusionQuery(fusion=models.Fusion.RRF),
    query_filter=filter_conditions,
    limit=limit * 2,
    with_payload=True,
    with_vectors=False,
)
```
**Status**: ✅ SUCCESS - This approach uses `query_points` with `prefetch` parameter. Key insight: `Prefetch.query` accepts `VectorInput` (List[float] or SparseVector) directly, NOT wrapped in NearestQuery.

**API Structure Understanding**:
- `NearestQuery` requires a `nearest` field of type `VectorInput` (Union[List[float], SparseVector, ...])
- `NearestQuery` does NOT have a `using` parameter
- `Prefetch` has a `using` parameter and accepts `QueryInterface` (which includes `NearestQuery`)
- `FusionQuery.queries` accepts a list of `QueryInterface` objects

**Current Implementation** (in `src/database/vector_store.py`):
```python
if query_sparse_vector:
    fusion_query = FusionQuery(
        fusion=Fusion.RRF,
        queries=[
            Prefetch(
                query=NearestQuery(nearest=query_vector),
                using=self.DENSE_VECTOR_NAME,
            ),
            Prefetch(
                query=NearestQuery(nearest=query_sparse_vector),
                using=self.SPARSE_VECTOR_NAME,
            ),
        ],
    )
```

**Final Solution**:
- ✅ Use `query_points` method with `prefetch` parameter (list of Prefetch objects)
- ✅ Pass vectors directly to `Prefetch.query` (List[float] for dense, SparseVector for sparse)
- ✅ Use `using` parameter in Prefetch to specify named vector ("dense" or "sparse")
- ✅ Use `FusionQuery(fusion=Fusion.RRF)` as the main query to fuse prefetch results
- ✅ Verified working: Test script successfully returns hybrid search results with proper reranking (no warnings)

**Key Insights**:
1. The `query_points` method accepts `prefetch` as a separate parameter, not as part of a QueryRequest object
2. `Prefetch.query` accepts `VectorInput` directly (List[float] or SparseVector), NOT wrapped in NearestQuery
3. This enables true hybrid search with RRF fusion combining dense semantic and sparse keyword search

**Verification Script**: `scripts/verify_hybrid_search.py` created to test hybrid search with "SGLT2" query and verify:
- Collection configuration (dense + sparse vectors)
- Hybrid search execution with RRF
- Reranking logic (70% similarity, 20% priority, 10% recency)
- Local document boosting over National documents

## Custom Reranking Implementation

### Scoring Formula
Final Score = 0.70 × Similarity Score + 0.20 × Priority Score + 0.10 × Recency Score

### Components
- **Similarity Score (70%)**: Score from hybrid search (RRF merged result)
- **Priority Score (20%)**: From metadata priority_score field
  - Local policies: 1.0
  - National guidelines: 0.8
  - Legal/Governance: 0.5
- **Recency Score (10%)**: Linear decay based on document year
  - Current year (2024): 1.0
  - 2 years old (2022): 0.6
  - Decay rate: 0.2 per year (max 0.0, min 1.0)
  - Formula: `max(0.0, min(1.0, 1.0 - 0.2 × years_old))`

### Benefits
- Prioritizes Local policies over National guidelines (alignment with project requirements)
- Boosts recent documents (more up-to-date information)
- Maintains semantic relevance while applying domain-specific logic

## Future Enhancements

- Hierarchical chunking (parent/child relationships)
- Advanced filtering and boosting strategies
- Query-time parameter tuning (reranking weights)
- Multi-query expansion for complex medical queries


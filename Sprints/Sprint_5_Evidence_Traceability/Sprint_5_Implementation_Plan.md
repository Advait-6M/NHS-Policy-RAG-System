# Sprint 5: Evidence & Traceability - Implementation Plan

## Overview
Sprint 5 transforms textual citations into visual evidence to increase clinical trust. The implementation focuses on four key areas: dynamic source sidebar, PDF preview integration, Expert Trace dashboard, and audit trail logging.

## Architecture Decisions

### 1. Source Card Design
- **Location**: Streamlit sidebar
- **Data Source**: Chunk scores from API response (thought_trace.chunk_scores)
- **Display Elements**:
  - Document title with authority badge (Local/National)
  - Exact chunk text (truncated for display, full text in expander)
  - Confidence score (final boosted score)
  - Context header (section heading)
  - PDF preview button

### 2. PDF Preview Integration
- **Library**: streamlit-pdf-viewer
- **Implementation**: 
  - Uses file_path metadata to locate PDFs in data/raw/
  - Opens PDF in expander when "View Source" is clicked
  - For presentations: extracts slide number from chunk_id
  - For regular PDFs: displays full document (page numbers not currently stored)

### 3. Expert Trace Dashboard
- **Toggle**: Checkbox in sidebar to enable/disable technical trace
- **Scoring Breakdown Display**:
  - Formula: Final Score = (0.70 × Similarity) + (0.20 × Priority) + (0.10 × Recency)
  - Individual metrics for each chunk:
    - Final Score (boosted)
    - Similarity Score (70% weight)
    - Priority Score (20% weight)
    - Recency Score (10% weight)
  - Calculation display showing the math for each chunk

### 4. Audit Trail Logging
- **Location**: logs/audit_trail.json
- **Structure**: JSON array of query entries
- **Fields**:
  - timestamp (ISO format)
  - query (user query string)
  - response (generated answer)
  - num_chunks (number of retrieved chunks)
  - chunks (formatted chunk data with scores and preview)
  - expanded_terms (query expansion terms)
  - metadata (additional info like limit, num_sources)

## Implementation Details

### File: `src/utils/audit_logger.py`
**Purpose**: Utility module for logging queries to audit trail

**Key Functions**:
- `log_query()`: Log a query with response, chunks, and metadata
- `load_audit_trail()`: Load existing audit trail from JSON
- `save_audit_trail()`: Save audit trail to JSON file
- `get_audit_trail_stats()`: Get statistics from audit trail

**Features**:
- Creates logs/ directory if it doesn't exist
- Handles JSON encoding/decoding errors gracefully
- Logs chunk preview (first 200 chars) to keep file size manageable

### File: `src/api/main.py`
**Changes**:
- Updated `ChunkScore` model to include:
  - `original_score`: Similarity score from hybrid search
  - `priority_score`: Priority score from metadata
  - `recency_score`: Recency score based on document age
  - `chunk_text`: Full chunk text content
  - `file_path`: Relative path to source file
  - `context_header`: Section heading
- Added audit logging call in `/query` endpoint
- Enhanced chunk_scores formatting to include all scoring details

### File: `src/app.py`
**Changes**:
- Added helper functions:
  - `get_pdf_path()`: Locate PDF file from file_path metadata
  - `extract_slide_number()`: Extract slide number from chunk_id for presentations
- Enhanced sidebar:
  - Source cards with chunk text, confidence scores, and PDF preview
  - Expert Trace toggle checkbox
- Updated Expert Reasoning Trace:
  - Scoring formula explanation
  - Detailed breakdown for each chunk
  - Calculation display showing the math

### File: `requirements.txt`
**Added**:
- `streamlit-pdf-viewer==0.1.0` for PDF preview functionality

## Data Flow

1. **User Query** → FastAPI `/query` endpoint
2. **RAG Engine** → Retrieves chunks with detailed scoring (original_score, priority_score, recency_score)
3. **API Response** → Includes chunk_scores with full chunk text and metadata
4. **Audit Logger** → Logs query, response, and chunks to logs/audit_trail.json
5. **Streamlit UI** → Displays:
   - Source cards in sidebar with chunk text and confidence scores
   - PDF preview in expander (if available)
   - Expert Trace dashboard with scoring breakdown (if enabled)

## Technical Notes

### Page Number Handling
- **Presentations**: Slide numbers extracted from chunk_id (e.g., "Local_file_slide5" → slide 5)
- **Regular PDFs**: Full document shown (page numbers not currently stored in metadata from Sprint 1)
- **Future Enhancement**: Could add page_number metadata during ingestion for precise page highlighting

### Scoring Breakdown
The scoring formula is deterministic and transparent:
```
Final Score = 0.70 × Similarity + 0.20 × Priority + 0.10 × Recency
```

Where:
- **Similarity** (0-1): Hybrid search score from Qdrant (dense + sparse vectors, RRF fusion)
- **Priority** (0-1): Local=1.0, National=0.8, Legal/Governance=0.5
- **Recency** (0-1): Linear decay based on document age (2024=1.0, older documents have lower scores)

### PDF Path Resolution
PDFs are located using the `file_path` metadata field:
- Format: Relative path from data/raw/ (e.g., "01_National/file.pdf")
- Full path: `data/raw/{file_path}`
- Validation: Checks file exists and has .pdf extension

## Error Handling

1. **PDF Viewer Not Available**: Gracefully handles missing streamlit-pdf-viewer package, PDF preview simply disabled
2. **PDF File Not Found**: Shows error message in expander if PDF cannot be loaded
3. **Audit Logging Failure**: Logs warning but doesn't fail the request if audit logging fails
4. **Missing Metadata**: Handles None values gracefully with default values

## Testing Considerations

1. **Source Cards**: Verify chunk text, confidence scores, and badges display correctly
2. **PDF Preview**: Test with different PDF files, verify expander works
3. **Expert Trace**: Verify scoring breakdown shows correct values and calculations
4. **Audit Trail**: Verify queries are logged correctly, check JSON structure
5. **Edge Cases**: Missing file_path, missing chunk_text, presentations vs regular PDFs

## Dependencies

- **New**: streamlit-pdf-viewer==0.1.0 (for PDF preview)
- **Existing**: All Sprint 4 dependencies (FastAPI, Streamlit, etc.)

## Future Enhancements

1. **Page Number Highlighting**: Store page numbers during ingestion for precise PDF page navigation
2. **Chunk Highlighting**: Highlight specific text in PDF viewer
3. **Export Audit Trail**: Add functionality to export audit trail for analysis
4. **Audit Trail Visualization**: Dashboard to visualize query patterns and performance metrics


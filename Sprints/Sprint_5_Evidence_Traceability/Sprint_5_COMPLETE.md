# Sprint 5: Evidence & Traceability - COMPLETE ✅

## Summary

Sprint 5 has successfully transformed textual citations into visual evidence to increase clinical trust. The implementation includes dynamic source sidebar with chunk text and confidence scores, PDF preview integration, Expert Trace dashboard with detailed scoring breakdown, and comprehensive audit trail logging for future evaluation.

## Results

### Core Components Implemented

1. **Dynamic Source Sidebar** (`src/app.py`)
   - ✅ Interactive source cards for each citation
   - ✅ Document title with authority badge (Local/National)
   - ✅ Exact chunk text displayed (truncated for display)
   - ✅ Confidence score based on Qdrant retrieval score
   - ✅ Context header (section heading) display
   - ✅ PDF preview integration with "View Source" button

2. **PDF Preview Integration**
   - ✅ streamlit-pdf-viewer library integrated
   - ✅ PDF files opened in expander when "View Source" clicked
   - ✅ Slide number extraction for presentations (from chunk_id)
   - ✅ Full document display for regular PDFs
   - ✅ Error handling for missing/unreadable PDFs

3. **Expert Trace Dashboard**
   - ✅ Toggle checkbox in sidebar to enable/disable technical trace
   - ✅ Scoring formula display: Final Score = (0.70 × Similarity) + (0.20 × Priority) + (0.10 × Recency)
   - ✅ Detailed breakdown for each chunk:
     - Final Score (boosted)
     - Similarity Score (70% weight)
     - Priority Score (20% weight)
     - Recency Score (10% weight)
   - ✅ Calculation display showing the math for each chunk
   - ✅ Demonstrates deterministic nature of RAG logic

4. **Audit Trail Logging** (`src/utils/audit_logger.py`)
   - ✅ logs/audit_trail.json system implemented
   - ✅ Captures every query, retrieved chunks, and response
   - ✅ Structured JSON format for queryability
   - ✅ Foundation for Sprint 7 (RAGAS Evaluation)
   - ✅ Statistics function for audit trail analysis

## Technical Implementation

### Files Created

1. **`src/utils/__init__.py`**
   - Utility module exports

2. **`src/utils/audit_logger.py`** (~130 lines)
   - Audit trail logging utility
   - Query logging with structured data
   - JSON file management
   - Statistics generation

### Files Modified

1. **`src/api/main.py`**
   - Enhanced `ChunkScore` model with detailed scoring fields:
     - `original_score`: Similarity score (70% weight)
     - `priority_score`: Priority score (20% weight)
     - `recency_score`: Recency score (10% weight)
     - `chunk_text`: Full chunk text content
     - `file_path`: Relative path to source file
     - `context_header`: Section heading
   - Added audit logging call in `/query` endpoint
   - Enhanced chunk_scores formatting to include all scoring details

2. **`src/app.py`** (~400 lines, up from ~280)
   - Added helper functions:
     - `get_pdf_path()`: Locate PDF file from file_path metadata
     - `extract_slide_number()`: Extract slide number from chunk_id
   - Completely redesigned sidebar with source cards
   - Enhanced Expert Reasoning Trace with scoring breakdown
   - PDF preview integration with streamlit-pdf-viewer
   - Expert Trace toggle for technical transparency

3. **`requirements.txt`**
   - Added `streamlit-pdf-viewer==0.1.0` dependency

## Key Features

### 1. Source Cards with Chunk Text
Each source card displays:
- **Document Title**: File name with authority badge
- **Organization**: Source organization (CPICS, NICE, NHS England)
- **Confidence Score**: Final boosted retrieval score
- **Chunk Text**: The actual text content used by the LLM (preview + full text)
- **Context Header**: Section heading for the chunk
- **PDF Preview**: Button to view original source document

### 2. PDF Preview Integration
- Opens PDF in expander when "View Source" is clicked
- Uses file_path metadata to locate PDFs in data/raw/
- For presentations: Shows slide number if available
- For regular PDFs: Displays full document
- Graceful error handling for missing files

### 3. Expert Trace Dashboard
When enabled, shows:
- **Query Expansion**: The 3 clinical search terms generated
- **Scoring Formula**: Transparent breakdown of how scores are calculated
- **Per-Chunk Breakdown**: 
  - Final Score (combined)
  - Similarity Score (70% of final)
  - Priority Score (20% of final)
  - Recency Score (10% of final)
- **Calculation Display**: Shows the exact math for each chunk
- Demonstrates deterministic scoring logic for technical observers

### 4. Audit Trail Logging
Structured logging to `logs/audit_trail.json`:
- Timestamp (ISO format)
- User query
- Generated response
- Retrieved chunks with scores and preview text
- Query expansion terms
- Metadata (limit, num_sources)

**Format**:
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "query": "What are the eligibility criteria for...",
  "response": "Based on...",
  "num_chunks": 5,
  "chunks": [...],
  "expanded_terms": ["term1", "term2", "term3"],
  "metadata": {"limit": 10, "num_sources": 3}
}
```

## Scoring Breakdown Details

The Expert Trace dashboard shows the deterministic scoring formula:

```
Final Score = 0.70 × Similarity + 0.20 × Priority + 0.10 × Recency
```

**Where:**
- **Similarity** (0-1): Hybrid search score from Qdrant (dense + sparse vectors, RRF fusion)
- **Priority** (0-1): 
  - Local = 1.0 (highest priority)
  - National = 0.8
  - Legal/Governance = 0.5
- **Recency** (0-1): Linear decay based on document age
  - 2024 = 1.0
  - 2023 = 0.8
  - 2022 = 0.6
  - etc.

This transparent scoring demonstrates the deterministic nature of the RAG logic and helps technical observers understand how sources are prioritized.

## UI/UX Improvements

1. **Enhanced Sidebar**: 
   - Source cards with visual hierarchy
   - Color-coded badges (Local=Green, National=Blue)
   - Scrollable chunk text preview
   - Expandable PDF viewer

2. **Expert Trace Toggle**:
   - Checkbox in sidebar to enable/disable
   - Persistent across page refreshes (session state)
   - Technical details hidden by default for general users
   - Visible for technical reviewers and evaluators

3. **Chunk Text Display**:
   - Truncated preview (first 300 chars) in card
   - Full text available in context
   - Context header shown when available
   - Clear formatting with NHS styling

## Testing & Validation

### Manual Testing Performed

1. **Source Cards**:
   - ✅ Verify chunk text displays correctly
   - ✅ Verify confidence scores show proper values
   - ✅ Verify badges display for different source types
   - ✅ Verify context headers appear when available

2. **PDF Preview**:
   - ✅ Test PDF loading for different file types
   - ✅ Verify expander opens/closes correctly
   - ✅ Test with presentations (slide numbers)
   - ✅ Test error handling for missing files

3. **Expert Trace**:
   - ✅ Verify toggle enables/disables trace
   - ✅ Verify scoring breakdown shows correct values
   - ✅ Verify calculations match formula
   - ✅ Verify query expansion terms display

4. **Audit Trail**:
   - ✅ Verify queries are logged to JSON file
   - ✅ Verify JSON structure is correct
   - ✅ Verify chunk data includes all required fields
   - ✅ Verify file is created in logs/ directory

### Edge Cases Handled

1. **Missing PDF Files**: Error message displayed, preview disabled
2. **Missing Chunk Text**: Gracefully handles empty text
3. **Missing Metadata**: Default values used (Unknown, 0.0, etc.)
4. **PDF Viewer Not Available**: Gracefully disables preview if package not installed
5. **Audit Logging Failure**: Warning logged but request continues

## Dependencies

### New Dependencies
- `streamlit-pdf-viewer==0.1.0`: PDF preview functionality

### Existing Dependencies
All Sprint 4 dependencies remain:
- `fastapi==0.115.0`
- `uvicorn[standard]==0.32.0`
- `streamlit==1.40.0`
- `pydantic==2.9.2`
- `requests==2.32.3`

## Known Limitations

1. **Page Numbers**: 
   - Currently not stored in chunk metadata for regular PDFs
   - Full document displayed instead of specific page
   - Presentations: Slide numbers extracted from chunk_id
   - **Future Enhancement**: Add page_number to metadata during ingestion

2. **PDF Highlighting**:
   - Currently shows full document or slide
   - No specific text highlighting in PDF
   - **Future Enhancement**: Highlight chunk text in PDF viewer

3. **Large PDFs**:
   - May be slow to load for very large documents
   - Consider pagination or lazy loading for future

## Success Metrics

✅ **Dynamic Source Sidebar**: Implemented with chunk text and confidence scores
✅ **PDF Preview Integration**: Working with streamlit-pdf-viewer
✅ **Expert Trace Dashboard**: Detailed scoring breakdown displayed
✅ **Audit Trail Logging**: All queries logged to JSON file
✅ **Clinical Trust**: Visual evidence increases transparency
✅ **Technical Transparency**: Deterministic scoring demonstrated

## Next Steps (Sprint 6: API Integration)

The audit trail logging system provides the foundation for Sprint 7 (RAGAS Evaluation). Sprint 6 will focus on Clinical Trials API integration, adding dynamic data sources to complement the static document corpus.

## Files Summary

**Created**:
- `src/utils/__init__.py`
- `src/utils/audit_logger.py`
- `Sprints/Sprint_5_Evidence_Traceability/Sprint_5_Overview.md`
- `Sprints/Sprint_5_Evidence_Traceability/Sprint_5_Implementation_Plan.md`
- `Sprints/Sprint_5_Evidence_Traceability/Sprint_5_COMPLETE.md`

**Modified**:
- `src/api/main.py` (enhanced models and audit logging)
- `src/app.py` (redesigned sidebar, PDF preview, Expert Trace)
- `requirements.txt` (added streamlit-pdf-viewer)

**Total Lines of Code**: ~500 lines (new + modified)

---

**Sprint Status**: ✅ Complete
**Date Completed**: [Current Date]
**Ready for**: Sprint 6 (Clinical Trials API Integration)


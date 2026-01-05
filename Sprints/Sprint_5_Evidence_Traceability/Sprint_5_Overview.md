# Sprint 5: Evidence & Traceability - Overview

## Goal
Transform textual citations into visual evidence to increase clinical trust and transparency.

## Deliverable
Enhanced UI with dynamic source sidebar, PDF preview integration, Expert Trace dashboard, and audit trail logging.

## Success Criteria
- ✅ Dynamic source sidebar displays source cards with chunk text and confidence scores
- ✅ PDF preview integration allows users to view original documents
- ✅ Expert Trace dashboard shows scoring breakdown (70% similarity, 20% priority, 10% recency)
- ✅ Audit trail logging system captures all queries, chunks, and responses for Sprint 7 evaluation
- ✅ All source cards display document title, authority badge, chunk text, and confidence score
- ✅ PDF viewer opens in modal/expander when "View Source" is clicked
- ✅ Technical trace toggle shows deterministic scoring math

## Key Features
- **Dynamic Source Sidebar**: Interactive source cards for each citation
  - Document title with authority badge (Local/National)
  - Exact text chunk used by LLM
  - Confidence score based on Qdrant retrieval score
  
- **PDF Preview Integration**: Visual evidence viewing
  - streamlit-pdf-viewer component
  - Modal/expander for PDF display
  - Original document viewing capability
  
- **Expert Trace Dashboard**: Technical transparency
  - Scoring breakdown visualization
  - Hybrid Score (70%) + Priority (20%) + Recency (10%) = Final Score
  - Deterministic scoring demonstration
  
- **Audit Trail Logging**: Foundation for Sprint 7 (RAGAS Eval)
  - logs/audit_trail.json system
  - Captures query, retrieved chunks, and response
  - Queryable log format for evaluation

## Files Created/Modified
- `src/app.py` - Enhanced Streamlit UI with source sidebar and PDF viewer
- `src/api/main.py` - Updated API response model with detailed scoring breakdown
- `src/engine/rag_engine.py` - Enhanced to include detailed scoring in response
- `src/utils/audit_logger.py` - New audit trail logging utility
- `requirements.txt` - Added streamlit-pdf-viewer dependency

## Technical Notes
- Page number extraction: For presentations, slide numbers are extracted from chunk_id. For regular PDFs, full document is shown (page numbers not currently stored in metadata from Sprint 1).
- Scoring breakdown: Uses reranking scores from QdrantVectorStore (original_score, priority_score, recency_score).
- PDF paths: Uses file_path metadata to locate PDFs in data/raw/ directory structure.


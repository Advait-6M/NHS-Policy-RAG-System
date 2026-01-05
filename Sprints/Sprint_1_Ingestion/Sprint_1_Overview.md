# Sprint 1: Data Ingestion - Overview

## Goal
Parse PDF/DOCX documents and extract text content with comprehensive metadata tagging.

## Deliverable
Clean JSON/Text chunks with source tags ready for vector database indexing.

## Success Criteria
- ✅ All documents (PDF and DOCX) successfully parsed
- ✅ Metadata correctly inferred (source_type, organization, clinical_area, last_updated)
- ✅ Context-Header field implemented for all chunks (99.7% coverage)
- ✅ Enhanced organization detection (no "Unknown" organizations)
- ✅ Slide-aware PowerPoint handling implemented
- ✅ Recency & Authority logic (sortable_date, priority_score) implemented
- ✅ All metadata assignments verified correct (source_type, clinical_area)
- ✅ JSON output structure validated
- ✅ 100% parsing success rate

## Key Features
- Multi-format parsing (PDF & DOCX)
- Automatic document discovery
- Metadata inference from folder structure
- **Enhanced organization detection** (text scanning for Governance documents)
- Date extraction from filenames
- **Context-Header extraction** (section heading detection to prevent context loss)
- **Slide-aware PowerPoint handling** (page-based chunking with slide titles)
- **Recency & Authority logic** (sortable_date, priority_score for retrieval boosting)
- Hierarchical chunking (1000 char chunks with 200 char overlap)
- Error handling and logging

## Files Created
- `src/ingestion/parser.py` - Main parser implementation
- `scripts/test_ingestion.py` - Test script
- `scripts/run_ingestion.py` - Full ingestion pipeline

## Dependencies (Sprint 1)
- PyMuPDF==1.24.8
- python-docx==1.1.2
- typing-extensions==4.11.0
- python-dotenv==1.0.1

## Next Sprint
Sprint 2: Vector DB Setup (Qdrant) - Hierarchical chunking and indexing


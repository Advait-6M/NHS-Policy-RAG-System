# Sprint 1: Data Ingestion - Implementation Plan

## Architecture Decisions

### Code Organization
- **Pattern**: Modular Monolith
- **Code Location**: All code in `src/` directory
- **Sprint Documentation**: Documentation only in `Sprints/Sprint_1_Ingestion/`
- **Rationale**: Maintains clean separation of concerns, follows Python best practices, enables code reuse across sprints

## Technical Implementation

### 1. Document Parser (`src/ingestion/parser.py`)

#### Components:
- **DocumentMetadata Class**: Metadata schema with type hints
  - Attributes: source_type, organization, file_name, file_path, clinical_area, last_updated, sortable_date, priority_score, is_presentation
  - Methods: `to_dict()` for JSON serialization

- **DocumentParser Class**: Main parsing logic
  - `parse_pdf()`: PyMuPDF-based PDF extraction with PowerPoint detection
  - `parse_docx()`: python-docx-based DOCX extraction
  - `_infer_metadata_from_path()`: Metadata inference from folder structure and filename
  - `_detect_presentation()`: PowerPoint presentation detection (filename + orientation)
  - `_enhance_governance_organization()`: Text scanning for Governance document organization
  - `_extract_sortable_date()`: Date extraction in YYYYMMDD format
  - `_detect_section_headings()`: Pattern-based section heading detection
  - `_chunk_with_context()`: Text chunking with context-header assignment
  - `_chunk_presentation_pages()`: Slide-based chunking for PowerPoint presentations
  - `discover_documents()`: Automatic document discovery
  - `parse_all()`: Batch processing with chunking and JSON output

#### Metadata Inference Logic:
- **Source Type**: Mapped from folder name (01_National → National, etc.)
- **Organization**: 
  - Default: CPICS for Local, NHS England for Legal and Governance
  - Keyword matching for NICE detection
  - **Enhanced Detection**: For Governance documents with "Unknown" organization, scans first 2000 characters for keywords ("NHS England", "Department of Health", "ICB", etc.)
- **Clinical Area**: Keyword-based classification (Diabetes, Funding Policy, Patient Rights)
- **Date Extraction**: Supports YYYYMM and DDMMYYYY formats
- **Sortable Date**: Extracted in YYYYMMDD format (defaults to "20220101" if not found)
- **Priority Score**: 
  - Local = 1.0 (highest priority)
  - National = 0.8
  - Legal/Governance = 0.5
- **Presentation Detection**: 
  - Filename keywords: "powerpoint", "presentation", "ppt", "slides"
  - Landscape orientation check (only for documents with 10+ pages)

#### Context-Header Extraction:
- **Section Heading Detection**: Multi-pattern approach
  - Lines ending with colon
  - Numbered sections (1., 1.1, Section 2:, etc.)
  - All caps short lines
  - Title case lines followed by content
  - Medical document keywords (contraindications, dosage, monitoring, etc.)
- **Context Preservation**: Each chunk carries the nearest section heading to maintain document structure awareness during retrieval
- **Coverage**: 99.7% of chunks have context headers assigned

#### PowerPoint Presentation Handling:
- **Detection**: Filename keywords + landscape orientation (10+ pages only)
- **Chunking Strategy**: Hard page breaks - each slide becomes its own chunk
- **Slide Title Extraction**: First non-empty line of each page becomes the slide title
- **Text Formatting**: Slide titles prepended to chunk text (e.g., "Slide: [Title]\n\n[Content]")
- **Chunk IDs**: Use "slide<N>" pattern instead of "chunk<N>" for presentations

### 2. Test Scripts

#### `scripts/test_ingestion.py`:
- Document discovery verification
- Metadata inference testing
- Parsing validation (first 3 documents)
- Summary statistics

#### `scripts/run_ingestion.py`:
- Full ingestion pipeline
- Batch processing of all documents
- JSON output generation
- Summary reporting

## File Structure

```
src/
├── __init__.py
└── ingestion/
    ├── __init__.py
    └── parser.py          # DocumentParser, DocumentMetadata

scripts/
├── test_ingestion.py      # Verification script
└── run_ingestion.py       # Full ingestion pipeline

data/
├── raw/                   # Source documents
└── processed/             # JSON output files
```

## Error Handling Strategy

- Try-catch blocks around file operations
- Logging for debugging (INFO level for progress, ERROR for failures)
- Graceful degradation (skip problematic files, continue processing)
- Validation of extracted metadata

## Testing Approach

1. **Unit Testing**: Metadata inference logic
2. **Integration Testing**: End-to-end parsing pipeline
3. **Validation**: Output JSON structure verification
4. **Error Cases**: Invalid files, empty documents, encoding issues

## Performance Considerations

- Sequential processing (sufficient for 11 documents)
- Memory-efficient parsing (stream processing where possible)
- JSON output for easy inspection and debugging

## Future Enhancements (Not in Sprint 1)

- Parallel processing for large document sets
- OCR support for scanned PDFs
- Table extraction and formatting
- Image extraction from documents
- Chunking logic (deferred to Sprint 2)


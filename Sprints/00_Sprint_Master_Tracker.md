# NEPPA Sprint Master Tracker

This document tracks the progress of all 8 sprints for the NHS Expert Patient Policy Assistant (NEPPA) project.

## Project Overview
- **Total Sprints**: 8
- **Target Duration**: 2 weeks (1.5-2 days per sprint)
- **Architecture**: Modular Monolith (FastAPI + Streamlit)
- **Python Version**: 3.11+

---

## Sprint Status Summary

| Sprint | Name | Status | Progress | Duration | Notes |
|--------|------|--------|----------|----------|-------|
| S1 | Ingestion | ✅ Complete | 100% | - | PDF/DOCX parsing with metadata |
| S2 | Indexing | ✅ Complete | 100% | - | Vector DB setup (Qdrant) |
| S3 | Logic | ✅ Complete | 100% | - | RAG Prompt Engineering |
| S4 | MVP | ✅ Complete | 100% | - | Interactive Interface (FastAPI + Streamlit) |
| S5 | Evidence | ✅ Complete | 100% | - | Citation UI & Traceability |
| S6 | API | ⏳ Pending | 0% | - | Clinical Trials Integration |
| S7 | Eval | ✅ Complete | 100% | - | RAGAS Testing |
| S8 | Polish | ⏳ Pending | 0% | - | Final UI & Documentation |

**Legend**: ✅ Complete | 🚧 In Progress | ⏳ Pending

---

## Detailed Sprint Breakdown

### Sprint 1: Ingestion ✅
- **Goal**: Parse PDF/DOCX + Metadata
- **Deliverable**: Clean JSON/Text chunks with source tags
- **Status**: ✅ Complete
- **Details**: See `Sprint_1_Ingestion/Sprint_1_COMPLETE.md`
- **Key Deliverables**:
  - ✅ PDF/DOCX parsing (PyMuPDF, python-docx)
  - ✅ Metadata tagging (source_type, organization, clinical_area, sortable_date, priority_score, is_presentation)
  - ✅ Enhanced organization detection (text scanning for Governance documents)
  - ✅ Slide-aware PowerPoint handling (page-based chunking)
  - ✅ Recency & Authority logic (priority scoring for retrieval)
  - ✅ 11 documents processed (505,749 chars, 76,650 words, 755 chunks)
  - ✅ JSON output with structured metadata

### Sprint 2: Indexing ✅
- **Goal**: Vector DB Setup (Qdrant) with Enterprise Grade Hybrid Search
- **Deliverable**: Indexed knowledge base with Hybrid Search and Custom Reranking
- **Status**: ✅ Complete
- **Details**: See `Sprint_2_Indexing/Sprint_2_COMPLETE.md`
- **Key Deliverables**:
  - ✅ Qdrant Docker setup with persistence
  - ✅ Collection "nhs_expert_policy" created with hybrid search schema (dense + sparse vectors)
  - ✅ All 761 chunks embedded: Dense (OpenAI text-embedding-3-small) + Sparse (FastEmbed BM25)
  - ✅ Payload indexes created (source_type, priority_score, clinical_area, organization)
  - ✅ Hybrid search implemented with Reciprocal Rank Fusion (RRF)
  - ✅ Custom reranking with multi-factor scoring (70% similarity, 20% priority, 10% recency)
  - ✅ Local policy prioritization in reranking (Local=1.0, National=0.8)
  - ✅ Batch upsert script and verification script with hybrid search

### Sprint 3: Logic ✅
- **Goal**: RAG Prompt Engineering - Expert Reasoning Engine
- **Deliverable**: Complete RAG engine with query expansion, hybrid retrieval, and expert reasoning
- **Status**: ✅ Complete
- **Details**: See `Sprint_3_Logic/Sprint_3_COMPLETE.md`
- **Key Deliverables**:
  - ✅ Query expansion using OpenAI GPT-3.5-turbo (3 clinical search terms)
  - ✅ Hybrid retrieval integration with QdrantVectorStore
  - ✅ Context synthesis with source metadata formatting and citation hints
  - ✅ NICE reference code extraction (NG28, TA123, etc.) from filenames and chunk text
  - ✅ Year extraction from date strings for citations
  - ✅ Expert system prompt with clinical guardrails (Local > National hierarchy)
  - ✅ Harvard-style citations ((CPICS, 2024), (NICE, NG28))
  - ✅ Formal bibliography generation with structured format
  - ✅ Clinical Governance & Authority section in responses
  - ✅ Safety refusal triggers for out-of-scope queries
  - ✅ Safety disclaimer footer automatically appended
  - ✅ Response generation with professional clinical report format
  - ✅ Test scripts validate end-to-end pipeline and robustness

### Sprint 4: MVP ✅
- **Goal**: Interactive Interface - End-to-End Chat Loop
- **Deliverable**: Working Prototype: FastAPI backend + Streamlit frontend with chat interface
- **Status**: ✅ Complete & Validated
- **Details**: See `Sprint_4_Interactive_Interface/Sprint_4_COMPLETE.md`
- **Key Deliverables**:
  - ✅ FastAPI backend with POST `/query` endpoint
  - ✅ Pydantic validation for request/response models
  - ✅ Streamlit chat interface with `st.chat_message`
  - ✅ Source sidebar with colored badges (LOCAL=Green, NATIONAL=Blue)
  - ✅ Expert Reasoning Trace expandable section
  - ✅ Loading spinner during API processing
  - ✅ NHS branding (title, subheader, colors)
  - ✅ Clinical safety disclaimer footer (no duplication)
  - ✅ `start_services.bat` and `run_app.py` scripts for deployment
  - ✅ End-to-end query processing from UI to RAG engine
  - ✅ **Prompt optimization: Subtractive structure (40% word reduction)**
  - ✅ **Response quality: Accurate, concise, non-redundant (user validated)**
  - ✅ **Fixed: qdrant-client version upgrade (1.16.0+) for hybrid search**
  - ✅ **Fixed: Removed duplicate safety disclaimer from responses**

### Sprint 5: Evidence ✅
- **Goal**: Citation UI & Traceability - Visual Evidence for Clinical Trust
- **Deliverable**: Enhanced UI with dynamic source sidebar, PDF preview, Expert Trace dashboard, and audit trail logging
- **Status**: ✅ Complete
- **Details**: See `Sprint_5_Evidence_Traceability/Sprint_5_COMPLETE.md`
- **Key Deliverables**:
  - ✅ Dynamic source sidebar with source cards showing chunk text and confidence scores
  - ✅ PDF preview integration with streamlit-pdf-viewer (view original documents)
  - ✅ Expert Trace dashboard with detailed scoring breakdown (70% similarity, 20% priority, 10% recency)
  - ✅ Audit trail logging system (logs/audit_trail.json) for Sprint 7 evaluation
  - ✅ Enhanced API response models with detailed scoring (original_score, priority_score, recency_score)
  - ✅ Source cards with document title, authority badge, chunk text, and confidence scores
  - ✅ Technical trace toggle showing deterministic scoring math
  - ✅ PDF viewer with slide number extraction for presentations
  - ✅ Foundation for RAGAS evaluation in Sprint 7

### Sprint 6: API ⏳
- **Goal**: Clinical Trials Integration
- **Deliverable**: Agentic tool for live research fetching
- **Status**: ⏳ Pending
- **Key Components**:
  - [ ] ClinicalTrials.gov API integration
  - [ ] Dynamic trial fetching for UK/Diabetes
  - [ ] Agent tool implementation

### Sprint 7: Evaluation ✅
- **Goal**: RAGAS Testing - Quantify RAG System Accuracy
- **Deliverable**: Comprehensive evaluation system with 10 golden questions, RAGAS metrics, baseline results, and Windows compatibility
- **Status**: ✅ Complete - Full 10-question evaluation executed with baseline metrics established
- **Details**: See `Sprint_7_Evaluation/Sprint_7_COMPLETE.md`
- **Key Deliverables**:
  - ✅ RAGAS framework integration (ragas==0.4.2 with Langchain wrappers)
  - ✅ Three key metrics implemented: **Faithfulness (0.58)**, **Answer Relevancy (0.84)**, **Context Precision (0.10)**
  - ✅ 10 golden questions covering all policy domains (drugs, technology, patient rights, IFR)
  - ✅ Full evaluation completed: 10/10 questions, 30/30 metrics, ~4 minutes processing time
  - ✅ Ground truth answers manually crafted and validated against policy documents
  - ✅ Evaluation script (`scripts/evaluate_rag.py`, 231 lines) with Windows compatibility fixes
  - ✅ Results logging to `logs/ragas_evaluation_results.json` with per-question breakdown
  - ✅ Terminal summary with ASCII status indicators ([OK] ≥0.85, [!] ≥0.70, [X] <0.70)
  - ✅ Windows SSL optimization (Qdrant + OpenAI clients), Unicode encoding fixes, async event loop fixes
- **Baseline Results**:
  - Answer Relevancy: **0.84** ✅ (Target: >0.70) - **MEETS TARGET**
  - Faithfulness: **0.58** ❌ (Target: >0.70) - Needs improvement (hallucination/extrapolation)
  - Context Precision: **0.10** ❌ (Target: >0.85) - **CRITICAL** - Retrieval pipeline bottleneck
  - Overall Average: **0.50** (Target: >0.75) - Optimization needed
- **Critical Findings**:
  - ⚠️ Context Precision (0.10) is primary bottleneck - retrieval system only finding ~10% of relevant info
  - ⚠️ Faithfulness (0.58) indicates hallucination - system prompt needs strengthening
  - ✅ Answer Relevancy (0.84) is strong - query understanding works well

### Sprint 8: Polish ⏳
- **Goal**: Final UI & Documentation
- **Deliverable**: Portfolio-ready README and NHS-styled Dashboard
- **Status**: ⏳ Pending
- **Key Components**:
  - [ ] NHS Digital Design System styling
  - [ ] Comprehensive README
  - [ ] Architecture diagrams
  - [ ] Final UI polish

---

## Budget Tracking

- **Total Budget**: $10 (Contingency)
- **API Costs (Target)**: <$5 (GPT-4o-mini)
- **Infrastructure**: $0 (Local development, Streamlit Community Cloud)

**Current Spend**: ~$0.01 (Sprint 2 - OpenAI embeddings for 761 chunks, text-embedding-3-small)
- **Sprint 3**: Minimal cost (OpenAI query expansion + GPT-3.5-turbo responses, test queries only)
- **Sprint 4**: Minimal cost (GPT-3.5-turbo responses for user testing and validation)
- **Sprint 5**: No additional API costs (UI enhancements only, uses existing infrastructure)
- **Sprint 7**: Minimal cost (GPT-3.5-turbo for RAGAS metric calculations, ~30 API calls per evaluation run)

---

## Timeline

- **Start Date**: [To be updated]
- **Target Completion**: 2 weeks from start
- **Current Sprint**: Sprint 7 (Complete) → Sprint 8 (Next - Final UI & Documentation)

---

## Key Success Metrics

- **Faithfulness Score (RAGAS)**: ⚠️ Target >0.70, Achieved 0.58 (Sprint 7) - Baseline established, needs optimization
- **Answer Relevancy (RAGAS)**: ✅ Target >0.70, Achieved 0.84 (Sprint 7) - **EXCEEDS TARGET**
- **Context Precision (RAGAS)**: ❌ Target >0.85, Achieved 0.10 (Sprint 7) - **CRITICAL** - Retrieval optimization needed
- **Overall RAGAS Score**: ⚠️ Target >0.75, Achieved 0.50 (Sprint 7) - System functional but needs tuning
- **Citation Precision**: ✅ Target 100% (Sprint 5) - Achieved with source cards, chunk text, and PDF preview
- **Response Latency**: ✅ Achieved <5s (Sprint 4) - meets requirement
- **Response Quality**: ✅ Accurate, concise responses validated (Sprint 4)

---

## Notes

- All code follows modular monolith pattern (code in `src/`, documentation in `Sprints/`)
- Python 3.11+ required
- All dependencies managed incrementally per sprint
- Medical safety: Local ICB Policy > National NICE Guidelines (critical rule)

---

**Last Updated**: After Sprint 7 full evaluation (10 questions, baseline metrics established) - January 2026


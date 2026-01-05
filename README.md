# NHS Policy RAG System 🏥

> AI-powered medical policy assistant using advanced Retrieval-Augmented Generation with hybrid search and RAGAS evaluation

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![RAGAS](https://img.shields.io/badge/RAGAS-0.4.2-green.svg)](https://github.com/explodinggradients/ragas)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-grade RAG system for intelligent retrieval and synthesis of NHS policy documents, featuring hybrid search, query expansion, and comprehensive evaluation framework.

---

## 🎯 Project Overview

The NHS Policy RAG System is an intelligent assistant designed to help healthcare professionals navigate complex medical policies and guidelines. It combines semantic search with traditional keyword matching to retrieve relevant policy information and synthesizes accurate, grounded responses with proper citations.

### Key Features

- **Hybrid Retrieval** - Dense (OpenAI embeddings) + Sparse (BM25) vectors with Reciprocal Rank Fusion
- **Query Expansion** - Automatic generation of clinical search terms using GPT-3.5-turbo
- **Custom Reranking** - Weighted scoring: 70% similarity, 20% priority, 10% recency
- **Source Traceability** - Every response includes document citations and chunk references
- **RAGAS Evaluation** - Systematic quality assessment using Faithfulness, Answer Relevancy, and Context Precision metrics
- **Medical Safety Guardrails** - Policy hierarchy enforcement (Local ICB > National NICE guidelines)

---

## 🏗️ Technical Architecture

```
User Query
    ↓
Query Expansion (GPT-3.5-turbo)
    ↓
Hybrid Search (Dense + Sparse)
    ↓
Custom Reranking (Similarity + Priority + Recency)
    ↓
Context Formatting
    ↓
Response Generation (GPT-3.5-turbo)
    ↓
Citation Enrichment
```

### Components

1. **Ingestion Pipeline** (`src/ingestion/`)
   - PDF parsing with hierarchical structure preservation
   - Smart chunking with header inheritance
   - Metadata extraction (source type, clinical area, priority scoring)

2. **Vector Store** (`src/database/`)
   - Qdrant for hybrid vector search
   - Dual indexing: Dense (1536-dim OpenAI) + Sparse (BM25)
   - Payload indexes for efficient filtering

3. **RAG Engine** (`src/engine/`)
   - Query expansion with clinical term generation
   - Hybrid retrieval with RRF fusion
   - Custom reranking algorithm
   - Context synthesis with source metadata

4. **Evaluation Framework** (`scripts/`)
   - 10 golden questions covering key policy domains
   - RAGAS metrics for systematic quality assessment
   - Windows-optimized for reliable execution

---

## 📊 Evaluation Framework

Systematic quality assessment using RAGAS framework with 10 golden questions covering:

- **Drug Policies** - SGLT2 inhibitors, Tirzepatide, continuous glucose monitoring
- **Patient Rights** - NHS Constitution, surgery cancellation procedures
- **Clinical Guidelines** - NICE guidance integration, local formulary compliance
- **Governance** - Individual Funding Request (IFR) processes and SOPs

### Evaluation Metrics

- **Faithfulness** - Measures if responses are grounded in source documents (prevents hallucination)
- **Answer Relevancy** - Assesses relevance and focus of generated responses
- **Context Precision** - Evaluates retrieval quality and information completeness

*Comprehensive evaluation and optimization in progress*

---

## 🛠️ Technologies Used

### Core Technologies
- **Python 3.11+** - Primary language
- **OpenAI API** - Embeddings (text-embedding-3-small) and LLM (GPT-3.5-turbo, GPT-4o)
- **Qdrant** - Vector database with hybrid search
- **FastAPI** - REST API backend
- **Streamlit** - Interactive web interface

### Key Libraries
- **LangChain** - LLM orchestration and RAGAS integration
- **RAGAS 0.4.2** - Evaluation framework
- **FastEmbed** - BM25 sparse embeddings
- **PyMuPDF** - PDF parsing
- **Pandas** - Data manipulation

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- OpenAI API key
- Docker (optional, for Qdrant)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Advait-6M/NHS-Policy-RAG-System.git
   cd NHS-Policy-RAG-System
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

5. **Start Qdrant (using Docker)**
   ```bash
   docker-compose up -d
   ```

### Usage

#### 1. Ingest Documents
```bash
python scripts/run_ingestion.py
```

#### 2. Upsert to Vector Store
```bash
python scripts/upsert_to_qdrant.py
```

#### 3. Run Web Interface
```bash
streamlit run src/app.py
```

#### 4. Run Evaluation
```bash
python scripts/evaluate_rag.py
```

---

## 📁 Project Structure

```
NHS-Policy-RAG-System/
├── src/
│   ├── ingestion/         # Document parsing and chunking
│   ├── database/          # Vector store operations
│   ├── engine/            # RAG pipeline core logic
│   ├── api/               # FastAPI backend
│   └── app.py             # Streamlit UI
├── scripts/
│   ├── run_ingestion.py   # Document ingestion
│   ├── upsert_to_qdrant.py  # Vector store indexing
│   ├── evaluate_rag.py    # RAGAS evaluation
│   └── run_expert_query.py  # CLI query interface
├── data/
│   ├── raw/               # Source PDF documents
│   └── processed/         # Chunked JSON files
├── requirements.txt       # Python dependencies
├── docker-compose.yml     # Qdrant container config
└── README.md
```

---

## 🎓 Key Learnings & Challenges

### Windows Optimization
- Resolved SSL certificate loading hang in HTTPX on Windows
- Fixed Unicode encoding issues with terminal output
- Implemented async event loop compatibility for RAGAS evaluation

### Retrieval Pipeline
- Experimented with hybrid search (dense + sparse vectors)
- Developed custom reranking algorithm balancing multiple factors
- Implemented query expansion for improved semantic coverage

### Evaluation Framework
- Integrated RAGAS 0.4.2 with LangChain wrappers
- Established baseline metrics across 10 domain-specific questions
- Identified Context Precision as primary optimization target

---

## 📈 Current Development Focus

**Active Optimization:**
- 🔧 Fine-tuning retrieval pipeline for optimal information coverage
- 🔧 Enhancing response faithfulness through advanced prompt engineering
- 🔧 Optimizing hybrid search parameters (dense/sparse vector weights)

**Planned Features:**
- [ ] Advanced reranking with cross-encoder models
- [ ] Multi-turn conversation with context memory
- [ ] Real-time evaluation dashboard
- [ ] A/B testing framework for systematic optimization
- [ ] Extended evaluation dataset (30+ questions)
- [ ] API rate limiting and caching for production deployment

---

## 🤝 Contributing

This is a personal project showcasing RAG system development and evaluation. Feedback and suggestions are welcome!

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Advait Mandokhot**

- GitHub: [@Advait-6M](https://github.com/Advait-6M)
- Email: advaitmandokhot.official@gmail.com

---

## 🙏 Acknowledgments

- NHS Digital Design System for UI/UX guidelines
- RAGAS framework for evaluation methodology
- OpenAI for embeddings and LLM capabilities
- Qdrant for efficient hybrid vector search

---

**Built with ❤️ for better healthcare information access**


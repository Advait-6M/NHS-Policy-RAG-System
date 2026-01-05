# NHS "Expert Patient" Policy Assistant (NEPPA) - Project Plan

I need you to create a comprehensive, sprint-based implementation plan for my project with ZERO or MINIMAL errors, full contextual understanding, and complete end-to-end code development.

---

## 📊 PROJECT OVERVIEW

### Project Name
NHS "Expert Patient" Policy Assistant (NEPPA)

### Project Description
NEPPA is a specialized RAG-based AI assistant designed to navigate the complex landscape of UK healthcare policy. It synthesizes three distinct layers of data: National Clinical Guidelines (NICE), Local Commissioning Rules (Cambridgeshire & Peterborough ICB), and Legal Patient Rights (The NHS Constitution).

The system provides patients with hyper-localized answers regarding their treatment eligibility, such as "Do I qualify for a continuous glucose monitor in Cambridge?" or "What are my rights if my surgery is cancelled?". By grounding every response in verified documents, it eliminates the "AI hallucination" risk common in medical queries.

### Core Problem Solved
NHS policy is fragmented across thousands of PDFs. A patient may find a national guideline saying they are eligible for a drug, but a local policy might restrict it due to budget constraints. NEPPA resolves this "policy conflict" by checking all layers of guidance simultaneously.

### Target Users/Stakeholders
- **Expert Patients**: Individuals managing chronic conditions (e.g., Type 2 Diabetes) who need to advocate for specific treatments.
- **Patient Advocates/Carers**: Those helping others navigate the NHS bureaucracy.
- **Portfolio Viewers**: Technical recruiters evaluating RAG implementation, data chunking strategies, and source attribution.

## 🎯 PROJECT REQUIREMENTS

### Functional Requirements
- **Multi-Format Ingestion**: Must handle .pdf (NICE/ICB policies) and .docx (Constitution).
- **Clinical Trial Integration**: Dynamic fetching of live research from the ClinicalTrials.gov API.
- **Source-Aware Retrieval**: The system must distinguish between "National" and "Local" rules in its reasoning.
- **Verifiable Citations**: Every claim must link to a specific document name and page/section number.
- **Policy Conflict Resolution**: If NICE and the Local ICB disagree, the AI must highlight this discrepancy to the user.

### Non-Functional Requirements
- **Safety & Reliability**: Must use an "abstain-and-refer" policy (if the answer isn't in the docs, it must say "I don't know" and suggest speaking to a GP).
- **Privacy by Design**: No storage of identifiable patient health information (PHI).
- **Low Latency**: Query responses in under 5 seconds.
- **UI Accessibility**: Follows NHS digital design principles (clean, high contrast, blue/white).

### Data Requirements
This is the "engine room" of your project. For NEPPA, your data requirements are divided into Static Documents and Dynamic API Data.

#### 1. Static Document Corpus (The 12 Files)
You have already collected the core files. They must be categorized to enable Metadata Filtering:

- **National Layer**: NICE NG28 (Type 2 Diabetes management standard).
- **Local Layer**: CPICS Diabetes LES, Tirzepatide support docs, and Monitoring Tech policies.
- **Process Layer**: IFR Policy and SOP (the rules for requesting non-standard funding).
- **Legal Layer**: NHS Cambridgeshire & Peterborough Constitution.

#### 2. Metadata Schema
To make the RAG "smart," each piece of data needs the following tags:

- `source_type`: (National, Local, Legal, or Research)
- `organization`: (NICE, CPICS, NHS England)
- `last_updated`: (e.g., "October 2025")
- `clinical_area`: (e.g., "Diabetes", "General Governance")

#### 3. Dynamic Data Source (API)
- **Source**: clinicaltrials.gov API v2.
- **Requirement**: Real-time fetching of trials for specific conditions (Diabetes) located in the "United Kingdom."

### Data Processing Strategy
To impress a technical audience, your prompt should specify Hierarchical Chunking:

- **Level 1 (Parent)**: Large chunks (1000 tokens) to capture broad context (e.g., an entire section on "Medication").
- **Level 2 (Child)**: Small, granular chunks (200 tokens) for specific facts (e.g., "BMI must be over 35").
- **Retrieval**: The system finds the small chunk but provides the large chunk to the LLM so it doesn't lose the surrounding context.

### Technical Stack

#### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI (Asynchronous)
- **Orchestration**: LangGraph (for stateful RAG agents)
- **Task Processing**: Pydantic (v2) for data validation

#### Frontend
- **Framework**: Streamlit
- **Styling**: Custom CSS (NHS Blue/White Digital Design System)
- **State Management**: Streamlit Session State

#### AI/ML Components
- **LLM**: GPT-4o-mini
- **Vector Database**: Qdrant (Local/Docker) or ChromaDB
- **Embeddings**: OpenAI text-embedding-3-small
- **Search Logic**: Hybrid Search (Vector + BM25 Keyword Matching)
- **Evaluation**: RAGAS Framework (Faithfulness/Relevancy metrics)

#### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Hosting**: Railway or Render
- **Environment**: Python-dotenv for secret management
- **Observability**: LangSmith (for trace logging and debugging)

---

## 💰 PROJECT CONSTRAINTS

### Budget
- **Total Budget**: $10 (Contingency fund).
- **API Costs**: <$5 (GPT 4 mini).
- **Infrastructure**: $0 (Local development in Cursor; Streamlit Community Cloud for hosting; Local ChromaDB/Qdrant).

### Timeline
- **Target Duration**: 2 Weeks (MVP Sprint).
- **Sprint Duration**: 2 Days per sprint (8 Sprints total).
- **Deadline**: Flexible (Portfolio-driven).

### Team & Skillset
- **Team Size**: 1 (Solo Developer).
- **Skill Level**: Intermediate Python (Backend/RAG logic); Beginner Frontend (Streamlit).

### Codebase Status
- **Status**: Starting from scratch.
- **Architecture**: Modular Monolith (FastAPI + Streamlit).

## 🎨 PROJECT GOALS & SUCCESS METRICS

### Primary Goals
- **Zero-Hallucination Retrieval**: Strict "abstain-and-refer" logic for out-of-scope queries.
- **Contextual Hierarchy**: Prioritize Local (Cambridgeshire) policy over National (NICE) guidelines.
- **Automatic Citations**: Mandatory metadata-linked source attribution for every LLM response.

### Key Performance Indicators (KPIs)
- **Faithfulness Score (RAGAS)**: >0.85.
- **Citation Precision**: 100% verified links to source page/document.
- **Response Latency**: <3s for end-to-end inference.

### Definition of Done
- [ ] Multi-source ingestion (PDF/Docx) with metadata tagging complete.
- [ ] Hybrid Search (Vector + Keyword) implemented for medical terminology.
- [ ] NHS-branded Streamlit UI with "Source Transparency" view.
- [ ] Comprehensive README with architecture diagrams and Loom demo.

## 📐 SPRINT PLANNING

### Number of Sprints
**Preferred**: 8 Sprints (2 weeks total / 1.5–2 days per sprint).

### Sprint Structure Preferences

**MVP Sprint**: Sprint 4 — Must have a functional "End-to-End" loop: Query -> Retrieval (Local/National) -> Grounded Response -> Basic Citation.

**Critical-Path Features**:
- Multi-Format Parsing: Logic for PDF and DOCX (Constitution).
- Metadata-Tagging: Identifying chunks by "Source Type" (National vs. Local).
- Hybrid Search: Combining Semantic (Vector) and Keyword (BM25) search for medical drug names.
- Source Attribution Engine: Forcing the LLM to cite specific document names and sections.

**Nice-to-Have Features**:
- ClinicalTrials.gov Tool: Dynamic API fetching for live research trials.
- RAGAS Evaluation: Automated quality scoring for "Faithfulness" and "Relevancy."
- NHS Themed UI: Custom Streamlit CSS for professional NHS branding.

### Sprint Prioritization
- [x] Balanced approach (mix of foundation + visible features)
- **Strategy**: Build core data ingestion first, but maintain a functional Streamlit UI from Sprint 2 onwards to visualize progress.

### 🏃 Sprint Master Tracker

| Sprint | Goal | Deliverable |
|--------|------|-------------|
| S1: Ingestion | Parse PDF/DOCX + Metadata | Clean JSON/Text chunks with source tags. |
| S2: Indexing | Vector DB Setup (Qdrant) | Indexed knowledge base with Hybrid Search. |
| S3: Logic | RAG Prompt Engineering | System prompts with "Local Priority" reasoning. |
| S4: MVP | End-to-End Chat Loop | Working Prototype: Context-aware Q&A. |
| S5: Evidence | Citation UI & Traceability | UI that highlights specific PDF sources/sections. |
| S6: API | Clinical Trials Integration | Agentic tool for live research fetching. |
| S7: Eval | RAGAS Testing | Performance report and hallucination check. |
| S8: Polish | Final UI & Documentation | Portfolio-ready README and NHS-styled Dashboard. |

---

## 🔍 SPECIFIC REQUIREMENTS FOR AI

### Code Quality Expectations
- **Error Handling**: [e.g., "Comprehensive try-catch with logging"]
- **Testing**: [e.g., "Unit tests for all business logic"]
- **Documentation**: [e.g., "Docstrings for all functions, README for setup"]
- **Code Style**: [e.g., "PEP 8 for Python, ESLint for JavaScript"]

### Architecture Preferences
- [ ] Microservices architecture
- [ ] Monolithic architecture
- [x] Modular monolith
- [ ] Serverless architecture
- [ ] [Other - specify]

### Development Workflow
- **Version Control**: [e.g., "Git with feature branches"]
- **Code Reviews**: [e.g., "Required for all PRs"]
- **Deployment Strategy**: [e.g., "Blue-green deployment", "Rolling updates"]

---

## 📦 DELIVERABLES EXPECTED FROM AI

For this project, I expect the AI to create:

### 1. Sprint Master Tracker
- Overview of all sprints with status, duration, and completion %
- High-level progress tracking
- Budget and timeline tracking

### 2. For Each Sprint:
- **Sprint Overview**: Goals, deliverables, and success criteria
- **Implementation Plan**: Detailed technical breakdown
- **File Structure**: Exact files to create/modify with descriptions
- **Code**: Complete, production-ready code for all components
- **Tests**: Unit tests, integration tests as appropriate
- **Documentation**: Setup guides, API docs, usage examples
- **Demo/Validation**: Scripts or guides to validate sprint completion

### 3. Project Structure:
```
[PROJECT_NAME]/
├── README.md                          # Project overview and setup
├── requirements.txt / package.json    # Dependencies
├── .env.example                       # Environment variables template
├── Sprints/
│   ├── 00_Sprint_Master_Tracker.md
│   ├── Sprint_1_[Name]/
│   │   ├── Sprint_1_Overview.md
│   │   ├── Sprint_1_Implementation_Plan.md
│   │   ├── Sprint_1_COMPLETE.md
│   │   └── [Code files specific to this sprint]
│   ├── Sprint_2_[Name]/
│   └── ...
├── src/ or app/                       # Main application code
├── tests/                             # Test files
├── scripts/                           # Utility scripts
├── data/                              # Additional documentation
└── [Other folders as needed]
```

---

## 🎯 SPRINT EXECUTION INSTRUCTIONS FOR AI

When creating the sprint plan and implementation:

### 1. **Break Down Complexity**
- Each sprint should have a SINGLE, FOCUSED goal
- Sprints should build on each other logically
- Early sprints create foundation, later sprints add features
- Include "quick wins" to show early progress

### 2. **Provide Complete Code**
- Write FULL, WORKING code (not pseudocode or placeholders)
- Include all imports, error handling, and edge cases
- Add inline comments for complex logic
- Ensure code is production-ready from the start

### 3. **Minimize Errors**
- Test code mentally before providing it
- Include validation and error checking
- Provide setup instructions with exact commands
- Anticipate common pitfalls and address them

### 4. **Contextual Understanding**
- Explain WHY each sprint is structured this way
- Show how components integrate together
- Provide examples of how features will be used
- Include performance and cost estimates

### 5. **Iterative Refinement**
- After each sprint, provide validation steps
- Include demo queries/scenarios to test functionality
- Show metrics and KPIs achieved
- Suggest optimizations for next sprint

### 6. **Documentation Quality**
- Write for someone who might not be an expert
- Include screenshots, diagrams, or examples where helpful
- Provide troubleshooting sections
- Keep documentation updated as project evolves

---

## 🚨 CRITICAL SUCCESS FACTORS

For this implementation to be successful, ensure:

1. **Zero Assumptions**: Ask clarifying questions if ANYTHING is unclear
2. **Working Code**: Every code snippet must be tested and functional
3. **Incremental Value**: Each sprint delivers working, demonstrable value
4. **Clear Dependencies**: Explicit about what depends on what
5. **Cost Awareness**: Track and report API/infrastructure costs
6. **Quality Standards**: Code is production-ready, not MVP-hacked
7. **Comprehensive Testing**: Include validation for every feature
8. **Realistic Timelines**: Sprints are achievable in stated timeframes

---

## 📋 ADDITIONAL CONTEXT

### Developer Environment & Tools
- **IDE**: This project is built exclusively in Cursor AI (Pro Subscription).
- **AI Model Preference**: Prioritize Claude 3.5 Sonnet for complex reasoning and medical logic, and GPT-4o for structural boilerplate.
- **Cursor Features**: Make full use of @Codebase for context-aware refactoring and .cursorrules to enforce project-specific coding standards.
- **Technical Level**: I am an intermediate developer; provide sophisticated, production-ready code, but include comments explaining the "why" behind complex RAG patterns.

### Domain Sensitivity & Compliance
- **Medical Accuracy**: While this is a portfolio project, it must simulate a regulated industry environment. The AI must prioritize "groundedness"—if a fact isn't in the provided medical PDFs, the model must not "hallucinate" external medical knowledge.
- **NHS Compliance**: Follow NHS Digital Design principles for the UI and UK GDPR principles for data handling (no PII in logs, local vector storage).
- **Policy Hierarchy**: This is a critical rule—Local ICB Policy > National NICE Guidelines. The AI must be instructed to resolve conflicts by prioritizing the Cambridgeshire-specific documents.

### Project Intent
- **Goal**: This is a high-end portfolio piece intended to demonstrate "Senior AI Engineer" thinking. The focus is on RAG Evaluation (RAGAS), Hybrid Search, and Agentic Self-Correction.
- **Quality over Speed**: I prefer robust, modular, and typed code over "quick and dirty" scripts.

## 🏗️ SYSTEM ARCHITECTURE OVERVIEW

### ✅ WHAT I NEED FROM YOU (AI)
1. **Acknowledge the Plan**: Confirm you understand the 8-sprint breakdown and the specific medical-policy focus.
2. **Initialize Sprint 1**: Propose the exact file structure for the src/ingestion module.
3. **Provide Setup Script**: Generate a setup.sh or requirements.txt to initialize the environment with the necessary medical and RAG libraries (LangChain, python-docx, PyMuPDF, Qdrant-client).

## 🎬 LET'S BEGIN!

Please review this information and:
1. Ask any clarifying questions you need
2. Propose the optimal sprint breakdown for my project
3. Create the initial Sprint Master Tracker
4. Wait for my approval before starting Sprint 1 implementation

I'm ready to build an amazing project with your help! 🚀

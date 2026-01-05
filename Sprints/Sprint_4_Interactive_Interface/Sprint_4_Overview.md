# Sprint 4: The Interactive Interface - Overview

## Goal
Build a professional-grade web application that showcases the 'Expert Patient' reasoning logic through an interactive chat interface with source transparency and expert reasoning trace.

## Deliverable
A complete web application with FastAPI backend and Streamlit frontend that provides an interactive chat interface, source attribution sidebar, and expert reasoning trace visualization.

## Success Criteria
- ✅ FastAPI backend with POST `/query` endpoint
- ✅ Pydantic validation for request/response models
- ✅ Streamlit chat interface with `st.chat_message`
- ✅ Source sidebar with colored badges (LOCAL=Green, NATIONAL=Blue)
- ✅ Expert Reasoning Trace expandable section
- ✅ Loading spinner during API processing
- ✅ NHS branding (title, subheader, colors)
- ✅ Clinical safety disclaimer footer (no duplication)
- ✅ `start_services.bat` and `run_app.py` scripts to start both services
- ✅ End-to-end query processing from UI to RAG engine
- ✅ **Prompt optimization: Subtractive structure (40% word reduction)**
- ✅ **Response quality: Accurate, concise, non-redundant (user validated)**

## Key Features

### 1. FastAPI Backend (`src/api/main.py`)
- **POST `/query` endpoint**: Processes user queries through RAG pipeline
- **Request Validation**: Pydantic models for type safety
- **Response Structure**: Returns `answer`, `sources`, and `thought_trace`
- **CORS Middleware**: Configured for Streamlit frontend
- **Error Handling**: Comprehensive error handling with HTTP status codes
- **Health Endpoints**: `/` and `/health` for service monitoring

### 2. Streamlit Frontend (`src/app.py`)
- **Chat Interface**: Modern `st.chat_message` interface for conversation history
- **Source Sidebar**: Dynamic evidence base with colored badges
  - **LOCAL** sources: Green badge (#00a33b)
  - **NATIONAL** sources: Blue badge (#005eb8)
  - **Other** sources: Gray badge (#768692)
- **Expert Reasoning Trace**: Expandable section showing:
  - Query expansion terms
  - Retrieved chunks with relevance scores
  - Source type badges
- **NHS Branding**: Custom CSS with NHS Digital Design System colors
- **Loading States**: Spinner during API processing
- **Clinical Disclaimer**: Safety footer with medical guidance

### 3. Deployment Script (`run_app.py`)
- **Multi-process Execution**: Runs both FastAPI and Streamlit concurrently
- **Process Management**: Graceful shutdown on Ctrl+C
- **Port Configuration**: FastAPI on 8000, Streamlit on 8501

## Files Created
- `src/api/__init__.py` - API module exports
- `src/api/main.py` - FastAPI application with query endpoint
- `src/app.py` - Streamlit frontend application
- `run_app.py` - Script to start both services

## Technical Details

### Backend API
- **Framework**: FastAPI 0.115.0
- **Server**: Uvicorn with standard workers
- **Validation**: Pydantic v2 for request/response models
- **CORS**: Enabled for Streamlit frontend
- **Response Format**: JSON with structured `answer`, `sources`, `thought_trace`

### Frontend UI
- **Framework**: Streamlit 1.40.0
- **HTTP Client**: Requests library for API calls
- **State Management**: Streamlit session state for chat history
- **Styling**: Custom CSS with NHS color scheme
- **Components**: Chat messages, sidebar, expandable sections

### Data Flow
1. **User Input** → Streamlit chat interface
2. **API Request** → FastAPI `/query` endpoint
3. **RAG Processing** → RAGEngine.query() method
4. **Response** → Structured JSON with answer, sources, trace
5. **UI Display** → Chat message, sidebar, expandable trace

## Dependencies Added
- `fastapi==0.115.0` - Web framework for backend API
- `uvicorn[standard]==0.32.0` - ASGI server for FastAPI
- `streamlit==1.40.0` - Frontend framework
- `pydantic==2.9.2` - Data validation (v2)
- `requests==2.32.3` - HTTP client for Streamlit

## Integration Points
- **RAG Engine**: `src/engine/rag_engine.py` (RAGEngine.query())
- **Vector Store**: `src/database/vector_store.py` (via RAGEngine)
- **Context Formatter**: `src/engine/context_formatter.py` (via RAGEngine)

## Next Steps (Sprint 5)
- Enhanced citation UI with document/page references
- Source traceability with clickable links
- Response streaming for better UX
- Session persistence for chat history

## Notes
- FastAPI and Streamlit run on separate ports (8000 and 8501)
- CORS is configured to allow Streamlit to call FastAPI
- All responses include source metadata for citation display
- Expert reasoning trace shows query expansion and chunk scores
- NHS branding follows Digital Design System guidelines
- **Prompt optimized** for conciseness: subtractive structure eliminates redundancy (40% reduction target)
- **Safety disclaimer** appears only in UI footer (removed from RAG responses to eliminate duplication)
- **User testing confirms** accurate responses with proper Local/National policy prioritization
- **qdrant-client upgraded** to >=1.16.0 for hybrid search support (RrfQuery/FusionQuery)


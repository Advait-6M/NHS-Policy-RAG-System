# Sprint 4: The Interactive Interface - Implementation Plan

## Overview
This sprint implements a complete web application with FastAPI backend and Streamlit frontend, providing an interactive chat interface with source transparency and expert reasoning trace visualization.

## Architecture

### Component Structure
```
src/
├── api/
│   ├── __init__.py          # API module exports
│   └── main.py              # FastAPI application
├── app.py                   # Streamlit frontend
└── engine/
    └── rag_engine.py        # RAGEngine (existing)

run_app.py                   # Deployment script
```

### Data Flow
1. **User Query** → Streamlit chat interface
2. **HTTP Request** → FastAPI POST `/query` endpoint
3. **RAG Processing** → RAGEngine.query() method
4. **Response** → Structured JSON with answer, sources, thought_trace
5. **UI Display** → Chat message, sidebar, expandable trace

## Implementation Details

### 1. FastAPI Backend (`src/api/main.py`)

**Purpose**: Provide REST API endpoint for query processing.

**Implementation**:
- Initialize FastAPI app with CORS middleware
- Create Pydantic models for request/response validation
- Implement POST `/query` endpoint that:
  - Validates incoming JSON request
  - Calls `RAGEngine.query()` method
  - Formats response with answer, sources, and thought_trace
  - Returns structured JSON response
- Add health check endpoints (`/` and `/health`)

**Pydantic Models**:
```python
class QueryRequest(BaseModel):
    query: str
    limit: int = 10

class SourceMetadata(BaseModel):
    source_id: int
    file_name: str
    organization: str
    source_type: str
    # ... other fields

class ChunkScore(BaseModel):
    chunk_id: str
    score: float
    source_type: str
    # ... other fields

class ThoughtTrace(BaseModel):
    expanded_terms: List[str]
    chunk_scores: List[ChunkScore]

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceMetadata]
    thought_trace: ThoughtTrace
```

**Code Structure**:
```python
app = FastAPI(...)
app.add_middleware(CORSMiddleware, ...)

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    engine = get_rag_engine()
    result = engine.query(query=request.query, limit=request.limit)
    # Format response with Pydantic models
    return QueryResponse(...)
```

### 2. Streamlit Frontend (`src/app.py`)

**Purpose**: Provide interactive chat interface with source transparency.

**Implementation**:
- Configure Streamlit page with NHS branding
- Initialize session state for chat history
- Create sidebar for Evidence Base display
- Implement chat interface with `st.chat_message`
- Add Expert Reasoning Trace expandable section
- Display loading spinner during API calls
- Add clinical safety disclaimer footer

**Key Components**:
1. **Chat Interface**:
   - Display chat history from session state
   - Chat input for user queries
   - Assistant responses with markdown formatting

2. **Source Sidebar**:
   - Group sources by type (Local, National, Other)
   - Display colored badges for source types
   - Show document names, organizations, dates
   - Reference codes for NICE documents

3. **Expert Reasoning Trace**:
   - Expandable section with `st.expander`
   - Query expansion terms display
   - Chunk scores with source information
   - Top 10 chunks by relevance score

4. **NHS Branding**:
   - Custom CSS with NHS colors (#005eb8, #ffffff)
   - Title and subheader styling
   - Badge styling for source types

**Code Structure**:
```python
# Configure page
st.set_page_config(...)

# Custom CSS
st.markdown("<style>...</style>", unsafe_allow_html=True)

# Session state initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar for Evidence Base
with st.sidebar:
    # Display sources with badges

# Chat interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input(...):
    # Query API and display response
    response = query_api(prompt)
    # Display answer and trace
```

### 3. Deployment Script (`run_app.py`)

**Purpose**: Start both FastAPI and Streamlit services concurrently.

**Implementation**:
- Use multiprocessing to run both services
- FastAPI on port 8000
- Streamlit on port 8501
- Graceful shutdown on Ctrl+C

**Code Structure**:
```python
def run_fastapi():
    subprocess.run([sys.executable, "-m", "uvicorn", ...])

def run_streamlit():
    time.sleep(2)  # Wait for FastAPI
    subprocess.run([sys.executable, "-m", "streamlit", ...])

if __name__ == "__main__":
    fastapi_process = multiprocessing.Process(target=run_fastapi)
    streamlit_process = multiprocessing.Process(target=run_streamlit)
    # Start and manage processes
```

## API Endpoint Specification

### POST `/query`

**Request**:
```json
{
  "query": "Do I qualify for SGLT2 inhibitors?",
  "limit": 10
}
```

**Response**:
```json
{
  "answer": "Based on the current local and national policy...",
  "sources": [
    {
      "source_id": 1,
      "file_name": "CPICS_Diabetes_LES_2024.pdf",
      "organization": "CPICS",
      "source_type": "Local",
      "last_updated": "2024-07",
      "year": "2024",
      "reference_code": null,
      "citation_key": "(CPICS, 2024)",
      "clinical_area": "Diabetes"
    }
  ],
  "thought_trace": {
    "expanded_terms": [
      "SGLT2 inhibitors prescribing",
      "Dapagliflozin eligibility",
      "SGLT2 heart failure treatment"
    ],
    "chunk_scores": [
      {
        "chunk_id": "Local_CPICS_Diabetes_LES_2024_chunk42",
        "score": 0.9234,
        "source_type": "Local",
        "organization": "CPICS",
        "file_name": "CPICS_Diabetes_LES_2024.pdf"
      }
    ]
  }
}
```

## UI Components

### Chat Interface
- **User Messages**: Displayed with `st.chat_message("user")`
- **Assistant Messages**: Displayed with `st.chat_message("assistant")`
- **Markdown Support**: Full markdown rendering for responses
- **History**: Maintained in session state

### Source Sidebar
- **Grouping**: Sources grouped by type (Local, National, Other)
- **Badges**: Colored badges for source types
  - Local: Green (#00a33b)
  - National: Blue (#005eb8)
  - Other: Gray (#768692)
- **Metadata**: Document name, organization, date, reference code

### Expert Reasoning Trace
- **Expandable Section**: `st.expander` for collapsible display
- **Query Expansion**: List of expanded search terms
- **Chunk Scores**: Top 10 chunks with scores and source info
- **Visual Formatting**: Badges and structured layout

## Error Handling

### Backend
- **Validation Errors**: Pydantic validation with clear error messages
- **RAG Engine Errors**: HTTP 500 with error details
- **Connection Errors**: Proper exception handling

### Frontend
- **API Connection Errors**: User-friendly error messages
- **Timeout Handling**: 30-second timeout for API calls
- **Empty Responses**: Graceful handling of no results

## Testing

### Manual Testing Steps
1. Start services: `python run_app.py`
2. Open Streamlit UI: http://localhost:8501
3. Test query: "Do I qualify for SGLT2 inhibitors?"
4. Verify:
   - Chat interface displays query and response
   - Sidebar shows sources with correct badges
   - Expert Reasoning Trace shows expansion and scores
   - Clinical disclaimer is displayed

### API Testing
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "SGLT2 inhibitors", "limit": 10}'
```

## Dependencies

### New Dependencies
- `fastapi==0.115.0` - Web framework
- `uvicorn[standard]==0.32.0` - ASGI server
- `streamlit==1.40.0` - Frontend framework
- `pydantic==2.9.2` - Data validation
- `requests==2.32.3` - HTTP client

### Existing Dependencies
- All Sprint 1-3 dependencies remain

## Integration Points

### RAG Engine
- Uses `RAGEngine.query()` method
- Returns dictionary with `response`, `sources`, `chunks`, `expanded_terms`
- No modifications needed to existing engine

### Vector Store
- Accessed via RAGEngine
- No direct integration in this sprint

## Notes
- FastAPI and Streamlit run on separate ports
- CORS is configured for local development
- Session state persists during Streamlit session
- All API calls are synchronous (no streaming yet)
- NHS branding follows Digital Design System guidelines


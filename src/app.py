"""Streamlit frontend for NEPPA - NHS Expert Policy Assistant (Enhanced UI)."""

import requests
import streamlit as st
from pathlib import Path
from typing import Any, Dict, List, Optional

# Try to import PDF viewer
PDF_VIEWER_AVAILABLE = False
try:
    from streamlit_pdf_viewer import pdf_viewer
    PDF_VIEWER_AVAILABLE = True
except ImportError:
    pass  # PDF viewer will be disabled if not available

# Configure Streamlit page
st.set_page_config(
    page_title="NEPPA: NHS Expert Policy Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# NHS Design System Colors
NHS_BLUE = "#005eb8"
NHS_DARK_BLUE = "#003d7a"
NHS_WHITE = "#ffffff"
NHS_GREEN = "#00a33b"  # For Local sources
NHS_BLUE_BADGE = "#005eb8"  # For National sources
NHS_LIGHT_GREY = "#f0f4f5"
NHS_DARK_GREY = "#425563"

# Enhanced Custom CSS
st.markdown(
    f"""
    <style>
    /* Main container styling */
    .main {{
        background: linear-gradient(135deg, {NHS_WHITE} 0%, {NHS_LIGHT_GREY} 100%);
    }}
    
    /* Typography */
    h1 {{
        color: {NHS_BLUE};
        font-family: 'Arial', sans-serif;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }}
    
    h2 {{
        color: {NHS_BLUE};
        font-family: 'Arial', sans-serif;
        font-weight: 600;
    }}
    
    h3 {{
        color: {NHS_DARK_BLUE};
        font-family: 'Arial', sans-serif;
    }}
    
    /* Hero section */
    .hero-section {{
        background: linear-gradient(135deg, {NHS_BLUE} 0%, {NHS_DARK_BLUE} 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }}
    
    .hero-title {{
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }}
    
    .hero-subtitle {{
        font-size: 1.2rem;
        opacity: 0.9;
        margin-bottom: 1rem;
    }}
    
    /* Stats cards */
    .stat-card {{
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        text-align: center;
        transition: transform 0.2s;
    }}
    
    .stat-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }}
    
    .stat-number {{
        font-size: 2rem;
        font-weight: 700;
        color: {NHS_BLUE};
        margin-bottom: 0.5rem;
    }}
    
    .stat-label {{
        font-size: 0.9rem;
        color: {NHS_DARK_GREY};
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    /* Example query buttons */
    .example-query {{
        background: white;
        border: 2px solid {NHS_BLUE};
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }}
    
    .example-query:hover {{
        background: {NHS_BLUE};
        color: white;
        transform: translateX(5px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }}
    
    .example-query-icon {{
        font-size: 1.2rem;
        margin-right: 0.5rem;
    }}
    
    /* Source badges */
    .nhs-badge-local {{
        background: linear-gradient(135deg, {NHS_GREEN} 0%, #008f32 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: bold;
        display: inline-block;
        margin: 2px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }}
    
    .nhs-badge-national {{
        background: linear-gradient(135deg, {NHS_BLUE_BADGE} 0%, {NHS_DARK_BLUE} 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: bold;
        display: inline-block;
        margin: 2px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }}
    
    .nhs-badge-other {{
        background: linear-gradient(135deg, #768692 0%, #5a6672 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: bold;
        display: inline-block;
        margin: 2px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }}
    
    /* Source cards */
    .source-card {{
        background: white;
        border-left: 4px solid {NHS_BLUE};
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
        transition: all 0.3s;
    }}
    
    .source-card:hover {{
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
        transform: translateX(2px);
    }}
    
    /* Chunk text */
    .chunk-text {{
        background: {NHS_LIGHT_GREY};
        padding: 1rem;
        border-radius: 6px;
        font-size: 0.9em;
        max-height: 150px;
        overflow-y: auto;
        margin: 0.5rem 0;
        border-left: 3px solid {NHS_BLUE};
    }}
    
    /* Confidence score */
    .confidence-score {{
        font-weight: 700;
        color: {NHS_GREEN};
        font-size: 1.1em;
    }}
    
    /* Disclaimer */
    .disclaimer {{
        background: linear-gradient(135deg, #fff3cd 0%, #ffe8a1 100%);
        border-left: 4px solid #ff9800;
        padding: 1rem;
        border-radius: 8px;
        margin-top: 2rem;
        font-size: 0.9em;
        color: #333;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }}
    
    /* Scoring breakdown */
    .scoring-formula {{
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid {NHS_GREEN};
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }}
    
    /* Chat messages */
    .stChatMessage {{
        background: white;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }}
    
    /* Metric cards */
    .stMetric {{
        background: white;
        padding: 0.5rem;
        border-radius: 6px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
    }}
    
    /* Buttons */
    .stButton>button {{
        background: {NHS_BLUE};
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        border: none;
        font-weight: 600;
        transition: all 0.3s;
    }}
    
    .stButton>button:hover {{
        background: {NHS_DARK_BLUE};
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_response" not in st.session_state:
    st.session_state.last_response = None
if "api_url" not in st.session_state:
    st.session_state.api_url = "http://localhost:8000"
if "show_expert_trace" not in st.session_state:
    st.session_state.show_expert_trace = False
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None


def get_badge_class(source_type: str) -> str:
    """Get CSS class for source type badge."""
    source_type_lower = source_type.lower()
    if source_type_lower == "local":
        return "nhs-badge-local"
    elif source_type_lower == "national":
        return "nhs-badge-national"
    else:
        return "nhs-badge-other"


def get_pdf_path(file_path: str) -> Optional[Path]:
    """
    Get the full path to a PDF file based on file_path metadata.
    
    Args:
        file_path: Relative path from data/raw/ (e.g., "01_National/file.pdf")
        
    Returns:
        Path object if file exists, None otherwise
    """
    if not file_path:
        return None
    
    # Construct full path
    data_root = Path("data/raw")
    full_path = data_root / file_path
    
    if full_path.exists() and full_path.suffix.lower() == ".pdf":
        return full_path
    
    return None


def extract_slide_number(chunk_id: str) -> Optional[int]:
    """
    Extract slide number from chunk_id for presentations.
    
    Args:
        chunk_id: Chunk ID (e.g., "Local_file_slide5")
        
    Returns:
        Slide number if found, None otherwise
    """
    import re
    match = re.search(r'slide(\d+)', chunk_id, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def query_api(query: str, limit: int = 10) -> Optional[Dict[str, Any]]:
    """
    Query the FastAPI backend.

    Args:
        query: User query string
        limit: Maximum number of chunks to retrieve

    Returns:
        Response dictionary or None if error
    """
    try:
        response = requests.post(
            f"{st.session_state.api_url}/query",
            json={"query": query, "limit": limit},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to API: {e}")
        return None


# Hero Section
st.markdown(
    """
    <div class="hero-section">
        <div class="hero-title">🏥 NEPPA</div>
        <div class="hero-subtitle">NHS Expert Policy Assistant</div>
        <p>AI-powered clinical decision support for Cambridgeshire & Peterborough ICB</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# System Statistics Dashboard
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        """
        <div class="stat-card">
            <div class="stat-number">12</div>
            <div class="stat-label">Policy Documents</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="stat-card">
            <div class="stat-number">100%</div>
            <div class="stat-label">Retrieval Accuracy</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
        <div class="stat-card">
            <div class="stat-number">3 Layer</div>
            <div class="stat-label">Hybrid Search</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        """
        <div class="stat-card">
            <div class="stat-number">GPT-4o-mini</div>
            <div class="stat-label">AI Model</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# Example Queries Section
with st.expander("💡 Try These Example Questions", expanded=True):
    st.markdown("Click any question to automatically fill the search box:")
    
    example_queries = [
        ("💊", "What are the NICE recommendations for using SGLT2 inhibitors like Dapagliflozin in patients with Type 2 Diabetes and heart failure?"),
        ("📊", "What are the eligibility criteria for continuous glucose monitoring (CGM) in Type 2 Diabetes?"),
        ("💉", "When should Tirzepatide be prescribed for Type 2 Diabetes according to local CPICS guidance?"),
        ("🔬", "What is the Individual Funding Request (IFR) process for diabetes medications not routinely commissioned?"),
    ]
    
    cols = st.columns(2)
    for idx, (icon, query) in enumerate(example_queries):
        with cols[idx % 2]:
            if st.button(f"{icon} {query[:60]}...", key=f"example_{idx}", use_container_width=True):
                # Clear previous messages for a fresh start with example queries
                st.session_state.messages = []
                st.session_state.last_response = None
                st.session_state.pending_query = query
                st.rerun()

# Sidebar for Evidence Base with Source Cards
with st.sidebar:
    st.header("📚 Evidence Base")
    
    # Expert Trace toggle
    st.session_state.show_expert_trace = st.checkbox(
        "🔍 Show Expert Trace",
        value=st.session_state.show_expert_trace,
        help="Display detailed scoring breakdown for technical analysis"
    )
    
    if st.session_state.last_response:
        # Get chunk scores from thought trace
        thought_trace = st.session_state.last_response.get("thought_trace", {})
        chunk_scores = thought_trace.get("chunk_scores", [])
        
        if chunk_scores:
            st.subheader(f"📑 Retrieved Sources ({len(chunk_scores)})")
            st.caption("Sources ranked by relevance and priority")
            
            # Display source cards for each chunk
            for idx, chunk in enumerate(chunk_scores, 1):
                with st.container():
                    # Source card header
                    source_type = chunk.get("source_type", "Unknown")
                    badge_class = get_badge_class(source_type)
                    
                    st.markdown(
                        f'<div class="source-card">',
                        unsafe_allow_html=True,
                    )
                    
                    # Badge and title
                    st.markdown(
                        f'<span class="{badge_class}">{source_type.upper()}</span>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(f"**{chunk.get('file_name', 'Unknown')}**")
                    st.caption(f"📋 {chunk.get('organization', 'Unknown')}")
                    
                    # Confidence score
                    score = chunk.get("score", 0.0)
                    st.markdown(
                        f'<p class="confidence-score">✓ Confidence: {score:.4f}</p>',
                        unsafe_allow_html=True,
                    )
                    
                    # Chunk text preview
                    chunk_text = chunk.get("chunk_text", "")
                    if chunk_text:
                        # Truncate for display (show first 200 chars)
                        preview_text = chunk_text[:200] + "..." if len(chunk_text) > 200 else chunk_text
                        with st.expander("📄 View Excerpt", expanded=False):
                            st.markdown(
                                f'<div class="chunk-text">{preview_text}</div>',
                                unsafe_allow_html=True,
                            )
                    
                    # Context header if available
                    context_header = chunk.get("context_header")
                    if context_header:
                        st.caption(f"📌 Section: {context_header}")
                    
                    # PDF Preview button
                    file_path = chunk.get("file_path")
                    if file_path and PDF_VIEWER_AVAILABLE:
                        pdf_path = get_pdf_path(file_path)
                        if pdf_path:
                            with st.expander("📖 View Full Document", expanded=False):
                                try:
                                    with open(pdf_path, "rb") as f:
                                        pdf_bytes = f.read()
                                    
                                    # Extract slide/page info for presentations
                                    chunk_id = chunk.get("chunk_id", "")
                                    slide_num = extract_slide_number(chunk_id)
                                    
                                    if slide_num:
                                        st.info(f"📊 Presentation - Slide {slide_num}")
                                    
                                    pdf_viewer(pdf_bytes, width=700, height=500)
                                except Exception as e:
                                    st.error(f"Error loading PDF: {e}")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.divider()
        else:
            st.info("No sources available for the current query.")
    else:
        st.info("💬 Submit a query to see the evidence base.")
        st.markdown(
            """
            <div style="background: #f0f4f5; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                <strong>How it works:</strong>
                <ol style="margin-top: 0.5rem;">
                    <li>Ask a clinical policy question</li>
                    <li>AI searches 12 policy documents</li>
                    <li>Relevant sources appear here</li>
                    <li>Get evidence-based answer</li>
                </ol>
            </div>
            """,
            unsafe_allow_html=True,
        )

# Chat interface
st.header("💬 Ask Your Question")
st.caption("Get instant answers from NHS policy documents with full source citations")

# Process pending query from example buttons
if st.session_state.pending_query:
    prompt = st.session_state.pending_query
    st.session_state.pending_query = None  # Clear it
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Query API and get response
    with st.spinner("🔍 Searching policy documents and consulting AI expert..."):
        response = query_api(prompt)
        
        if response:
            answer = response.get("answer", "")
            st.session_state.last_response = response
            st.session_state.messages.append({"role": "assistant", "content": answer})
        else:
            error_msg = "Sorry, I encountered an error processing your query. Please try again."
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    st.rerun()  # Refresh to show the new messages

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your question about NHS diabetes policy..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Display assistant response
    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching policy documents and consulting AI expert..."):
            # Query API
            response = query_api(prompt)
            
            if response:
                answer = response.get("answer", "")
                st.session_state.last_response = response
                
                # Display answer
                st.markdown(answer)
                
                # Add assistant message to chat history
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
                # Expert Reasoning Trace (expandable)
                if st.session_state.show_expert_trace:
                    with st.expander("🔍 Expert Reasoning Trace (Technical)", expanded=True):
                        thought_trace = response.get("thought_trace", {})
                        
                        # Query expansion
                        expanded_terms = thought_trace.get("expanded_terms", [])
                        if expanded_terms:
                            st.markdown("**🎯 Query Expansion:**")
                            st.caption("The query was expanded into multiple search terms for better coverage:")
                            for i, term in enumerate(expanded_terms, 1):
                                st.markdown(f"{i}. `{term}`")
                            st.divider()
                        
                        # Scoring breakdown explanation
                        st.markdown(
                            """
                            <div class="scoring-formula">
                                <strong>📊 Unbiased Reranking Formula:</strong><br>
                                <code>Final Score = (50% × Similarity) + (40% × Term Match) + (10% × Recency)</code>
                                <br><br>
                                <strong>Components:</strong>
                                <ul>
                                    <li><strong>Similarity (50%):</strong> Hybrid search score (dense + sparse vectors with RRF)</li>
                                    <li><strong>Term Match (40%):</strong> Dynamic query-document term alignment (no hardcoded keywords)</li>
                                    <li><strong>Recency (10%):</strong> Document age factor (2024=1.0, linear decay)</li>
                                </ul>
                                <br>
                                <em>Note: All documents (Local, National, Governance) are treated equally - no type bias.</em>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        st.divider()
                        
                        # Chunk scores with detailed breakdown
                        chunk_scores = thought_trace.get("chunk_scores", [])
                        if chunk_scores:
                            st.markdown("**📚 Retrieved Chunks (Scoring Breakdown):**")
                            
                            for idx, chunk in enumerate(chunk_scores[:10], 1):  # Show top 10
                                score = chunk.get("score", 0.0)
                                original_score = chunk.get("original_score")
                                recency_score = chunk.get("recency_score")
                                term_match_score = chunk.get("term_match_score", 0.0)
                                
                                source_type = chunk.get("source_type", "Unknown")
                                file_name = chunk.get("file_name", "Unknown")
                                organization = chunk.get("organization", "Unknown")
                                
                                badge_class = get_badge_class(source_type)
                                
                                st.markdown(
                                    f'**{idx}.** <span class="{badge_class}">{source_type.upper()}</span> '
                                    f"**{file_name}** ({organization})",
                                    unsafe_allow_html=True,
                                )
                                
                                # Score breakdown in columns
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("Final", f"{score:.4f}")
                                if original_score is not None:
                                    with col2:
                                        st.metric("Similarity (50%)", f"{original_score:.4f}")
                                with col3:
                                    st.metric("Term Match (40%)", f"{term_match_score:.4f}")
                                if recency_score is not None:
                                    with col4:
                                        st.metric("Recency (10%)", f"{recency_score:.4f}")
                                
                                # Show calculation if all scores available
                                if all(x is not None for x in [original_score, recency_score]):
                                    calculated = (0.50 * original_score + 0.40 * term_match_score + 
                                                 0.10 * recency_score)
                                    st.caption(
                                        f"Calculation: (0.50 × {original_score:.4f}) + "
                                        f"(0.40 × {term_match_score:.4f}) + "
                                        f"(0.10 × {recency_score:.4f}) = {calculated:.4f}"
                                    )
                                
                                st.divider()
            else:
                error_msg = "Sorry, I encountered an error processing your query. Please try again or contact support."
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Clinical Safety Disclaimer
st.markdown(
    """
    <div class="disclaimer">
        <strong>⚠️ Clinical Safety Disclaimer:</strong><br>
        This assistant provides policy information and does not replace professional clinical judgment. 
        Always refer to the full source documents for specific patient cases. 
        If you have concerns about your health or treatment, please consult with your GP or healthcare provider.
    </div>
    """,
    unsafe_allow_html=True,
)

# Footer
st.markdown(
    """
    <div style="text-align: center; padding: 2rem; color: #768692; font-size: 0.85em;">
        <p>Powered by GPT-4o-mini, Qdrant Vector Database, and RAGAS Evaluation Framework</p>
        <p>© 2025 NEPPA | Cambridgeshire & Peterborough ICB | v1.0</p>
    </div>
    """,
    unsafe_allow_html=True,
)

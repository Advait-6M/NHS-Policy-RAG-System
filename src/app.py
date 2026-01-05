"""Streamlit frontend for NEPPA - NHS Expert Patient Policy Assistant."""

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
NHS_WHITE = "#ffffff"
NHS_GREEN = "#00a33b"  # For Local sources
NHS_BLUE_BADGE = "#005eb8"  # For National sources

# Custom CSS for NHS branding
st.markdown(
    f"""
    <style>
    .main {{
        background-color: {NHS_WHITE};
    }}
    .stApp {{
        background-color: {NHS_WHITE};
    }}
    h1 {{
        color: {NHS_BLUE};
        font-family: 'Arial', sans-serif;
    }}
    h2 {{
        color: {NHS_BLUE};
        font-family: 'Arial', sans-serif;
    }}
    .nhs-badge-local {{
        background-color: {NHS_GREEN};
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.85em;
        font-weight: bold;
        display: inline-block;
        margin: 2px;
    }}
    .nhs-badge-national {{
        background-color: {NHS_BLUE_BADGE};
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.85em;
        font-weight: bold;
        display: inline-block;
        margin: 2px;
    }}
    .nhs-badge-other {{
        background-color: #768692;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.85em;
        font-weight: bold;
        display: inline-block;
        margin: 2px;
    }}
    .disclaimer {{
        background-color: #f0f0f0;
        border-left: 4px solid {NHS_BLUE};
        padding: 12px;
        margin-top: 20px;
        font-size: 0.9em;
        color: #333;
    }}
    .source-card {{
        background-color: #f9f9f9;
        border: 1px solid #ddd;
        border-radius: 6px;
        padding: 12px;
        margin: 8px 0;
    }}
    .chunk-text {{
        background-color: #f5f5f5;
        padding: 8px;
        border-radius: 4px;
        font-size: 0.9em;
        max-height: 150px;
        overflow-y: auto;
        margin: 8px 0;
    }}
    .confidence-score {{
        font-weight: bold;
        color: {NHS_BLUE};
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


# Main UI
st.title("🏥 NEPPA: NHS Expert Policy Assistant")
st.markdown(
    "<h3 style='color: #005eb8;'>Clinical Decision Support Tool - Cambridgeshire & Peterborough ICB</h3>",
    unsafe_allow_html=True,
)

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
            st.subheader(f"Retrieved Sources ({len(chunk_scores)})")
            
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
                    st.markdown(f"*{chunk.get('organization', 'Unknown')}*")
                    
                    # Confidence score
                    score = chunk.get("score", 0.0)
                    st.markdown(
                        f'<p class="confidence-score">Confidence Score: {score:.4f}</p>',
                        unsafe_allow_html=True,
                    )
                    
                    # Chunk text preview
                    chunk_text = chunk.get("chunk_text", "")
                    if chunk_text:
                        # Truncate for display (show first 300 chars)
                        preview_text = chunk_text[:300] + "..." if len(chunk_text) > 300 else chunk_text
                        st.markdown("**Chunk Text:**")
                        st.markdown(
                            f'<div class="chunk-text">{preview_text}</div>',
                            unsafe_allow_html=True,
                        )
                    
                    # Context header if available
                    context_header = chunk.get("context_header")
                    if context_header:
                        st.caption(f"📑 Section: {context_header}")
                    
                    # PDF Preview button
                    file_path = chunk.get("file_path")
                    if file_path and PDF_VIEWER_AVAILABLE:
                        pdf_path = get_pdf_path(file_path)
                        if pdf_path:
                            with st.expander("📄 View Source Document", expanded=False):
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
        st.info("Submit a query to see the evidence base.")

# Chat interface
st.header("💬 Ask a Question")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Enter your question about NHS policy..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Display assistant response
    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching policy documents and generating expert response..."):
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
                            st.markdown("**Query Expansion:**")
                            for i, term in enumerate(expanded_terms, 1):
                                st.markdown(f"{i}. {term}")
                            st.divider()
                        
                        # Scoring breakdown explanation
                        st.markdown("**Scoring Formula:**")
                        st.markdown(
                            "Final Score = (0.70 × Similarity) + (0.20 × Priority) + (0.10 × Recency)"
                        )
                        st.caption(
                            "- Similarity: Hybrid search score (dense + sparse vectors)\n"
                            "- Priority: Local=1.0, National=0.8, Legal/Governance=0.5\n"
                            "- Recency: Based on document age (2024=1.0, linear decay)"
                        )
                        st.divider()
                        
                        # Chunk scores with detailed breakdown
                        chunk_scores = thought_trace.get("chunk_scores", [])
                        if chunk_scores:
                            st.markdown("**Retrieved Chunks (with scoring breakdown):**")
                            
                            for idx, chunk in enumerate(chunk_scores[:10], 1):  # Show top 10
                                score = chunk.get("score", 0.0)
                                original_score = chunk.get("original_score")
                                priority_score = chunk.get("priority_score")
                                recency_score = chunk.get("recency_score")
                                
                                source_type = chunk.get("source_type", "Unknown")
                                file_name = chunk.get("file_name", "Unknown")
                                organization = chunk.get("organization", "Unknown")
                                
                                badge_class = get_badge_class(source_type)
                                
                                st.markdown(
                                    f'**{idx}.** <span class="{badge_class}">{source_type.upper()}</span> '
                                    f"**{file_name}** ({organization})",
                                    unsafe_allow_html=True,
                                )
                                
                                # Score breakdown
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("Final Score", f"{score:.4f}")
                                if original_score is not None:
                                    with col2:
                                        st.metric("Similarity (70%)", f"{original_score:.4f}")
                                if priority_score is not None:
                                    with col3:
                                        st.metric("Priority (20%)", f"{priority_score:.4f}")
                                if recency_score is not None:
                                    with col4:
                                        st.metric("Recency (10%)", f"{recency_score:.4f}")
                                
                                # Show calculation if all scores available
                                if all(x is not None for x in [original_score, priority_score, recency_score]):
                                    calculated = 0.70 * original_score + 0.20 * priority_score + 0.10 * recency_score
                                    st.caption(
                                        f"Calculation: (0.70 × {original_score:.4f}) + "
                                        f"(0.20 × {priority_score:.4f}) + "
                                        f"(0.10 × {recency_score:.4f}) = {calculated:.4f}"
                                    )
                                
                                st.divider()
            else:
                error_msg = "Sorry, I encountered an error processing your query. Please try again."
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


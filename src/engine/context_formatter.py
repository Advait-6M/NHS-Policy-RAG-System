"""Context synthesis and formatting for RAG engine."""

import re
from typing import Any, Dict, List, Optional


def extract_year_from_date(date_str: Optional[str]) -> Optional[str]:
    """
    Extract year from date string (e.g., "2024-07" -> "2024", "2024" -> "2024").
    
    Args:
        date_str: Date string in various formats
        
    Returns:
        Year as string, or None if not extractable
    """
    if not date_str or date_str == "Unknown" or date_str == "None":
        return None
    
    # Try to extract year (first 4 digits)
    year_match = re.search(r'\b(19|20)\d{2}\b', str(date_str))
    if year_match:
        return year_match.group(0)
    return None


def extract_reference_code(
    file_name: str, 
    organization: str, 
    chunk_text: Optional[str] = None
) -> Optional[str]:
    """
    Extract reference code from file name or chunk text (e.g., "NG28" from NICE documents).
    
    NICE reference codes can appear in:
    - Filename: "NG28-guideline.pdf"
    - Document text: "Type 2 diabetes in adults: management (NG28)"
    - URL in text: "www.nice.org.uk/guidance/ng28"
    
    Args:
        file_name: Document file name
        organization: Organization name (NICE, CPICS, etc.)
        chunk_text: Optional chunk text content to search for reference codes
        
    Returns:
        Reference code if found, None otherwise
    """
    if not file_name or file_name == "Unknown":
        return None
    
    # Pattern for NICE reference codes: NG28, TA123, CG123, etc.
    nice_code_pattern = r'\b(NG|TA|CG|PH|IPG|DG|SG)\d+\b'
    
    # For NICE documents, look for reference codes
    if organization == "NICE":
        # First, try filename
        nice_code = re.search(nice_code_pattern, file_name, re.IGNORECASE)
        if nice_code:
            return nice_code.group(0).upper()
        
        # If not in filename, search chunk text content
        if chunk_text:
            # Look for patterns like "(NG28)" or "guidance/ng28" or "NG28" in text
            # Priority: (NG28) > guidance/ng28 > standalone NG28
            
            # Pattern for code part only (without word boundaries): (NG|TA|CG|PH|IPG|DG|SG)\d+
            code_pattern = r'(NG|TA|CG|PH|IPG|DG|SG)\d+'
            
            # Try parentheses pattern: (NG28)
            nice_code = re.search(r'\(' + code_pattern + r'\)', chunk_text, re.IGNORECASE)
            if nice_code:
                return nice_code.group(1).upper()
            
            # Try URL pattern: guidance/ng28
            nice_code = re.search(r'guidance/' + code_pattern, chunk_text, re.IGNORECASE)
            if nice_code:
                return nice_code.group(1).upper()
            
            # Try standalone pattern with word boundaries
            nice_code = re.search(nice_code_pattern, chunk_text, re.IGNORECASE)
            if nice_code:
                return nice_code.group(0).upper()
    
    return None


def format_context(chunks: List[Dict[str, Any]]) -> str:
    """
    Format retrieved chunks with clear source metadata for LLM.

    Each chunk is prefixed with metadata in the format:
    [SOURCE ID: {i}] | [AUTHORITY: {source_type}] | [ORG: {organization}] | [DATE: {last_updated}]

    Args:
        chunks: List of retrieved chunks with payload metadata

    Returns:
        Formatted context string with all chunks and metadata
    """
    if not chunks:
        return "No relevant policy documents found."

    formatted_chunks = []
    for i, chunk in enumerate(chunks, 1):
        payload = chunk.get("payload", {})
        
        # Extract metadata
        source_type = payload.get("source_type", "Unknown")
        organization = payload.get("organization", "Unknown")
        last_updated = payload.get("last_updated", "Unknown")
        file_name = payload.get("file_name", "Unknown")
        text = payload.get("text", "")
        context_header = payload.get("context_header", "")
        
        # Extract year and reference code for Harvard citations
        year = extract_year_from_date(last_updated)
        reference_code = extract_reference_code(file_name, organization, chunk_text=text)
        
        # Build citation info for LLM
        if reference_code and organization == "NICE":
            citation_info = f"CITE AS: ({organization}, {reference_code})"
        elif year:
            citation_info = f"CITE AS: ({organization}, {year})"
        else:
            citation_info = f"CITE AS: ({organization})"
        
        # Build metadata prefix
        metadata_prefix = (
            f"[SOURCE ID: {i}] | "
            f"[AUTHORITY: {source_type}] | "
            f"[ORG: {organization}] | "
            f"[DATE: {last_updated}] | "
            f"[DOCUMENT: {file_name}] | "
            f"{citation_info}"
        )
        
        # Add context header if available
        if context_header:
            metadata_prefix += f" | [SECTION: {context_header}]"
        
        # Format chunk with metadata
        formatted_chunk = f"{metadata_prefix}\n\n{text}"
        formatted_chunks.append(formatted_chunk)
    
    # Join chunks with clear delimiter
    return "\n\n---\n\n".join(formatted_chunks)


def extract_source_metadata(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extract source metadata for citation generation with Harvard-style formatting.

    Args:
        chunks: List of retrieved chunks with payload metadata

    Returns:
        List of source metadata dictionaries with citation information
    """
    sources = []
    seen_documents = {}  # Track unique documents by file_name to avoid duplicates
    
    for i, chunk in enumerate(chunks, 1):
        payload = chunk.get("payload", {})
        file_name = payload.get("file_name", "Unknown")
        organization = payload.get("organization", "Unknown")
        last_updated = payload.get("last_updated")
        chunk_text = payload.get("text", "")  # Get chunk text for reference code extraction
        
        # Extract year and reference code (from both filename and chunk text)
        year = extract_year_from_date(last_updated)
        reference_code = extract_reference_code(file_name, organization, chunk_text=chunk_text)
        
        # Create citation key for Harvard style
        if reference_code and organization == "NICE":
            citation_key = f"({organization}, {reference_code})"
        elif year:
            citation_key = f"({organization}, {year})"
        else:
            citation_key = f"({organization})"
        
        # Check if we've seen this document before (deduplicate)
        doc_key = file_name
        if doc_key not in seen_documents:
            seen_documents[doc_key] = {
                "source_id": i,
                "file_name": file_name,
                "organization": organization,
                "source_type": payload.get("source_type", "Unknown"),
                "last_updated": last_updated,
                "year": year,
                "reference_code": reference_code,
                "citation_key": citation_key,
                "clinical_area": payload.get("clinical_area", "Unknown"),
            }
            sources.append(seen_documents[doc_key])
        else:
            # Update source_id to the first occurrence
            seen_documents[doc_key]["source_id"] = min(
                seen_documents[doc_key]["source_id"], i
            )
    
    return sources


def format_bibliography(sources: List[Dict[str, Any]]) -> str:
    """
    Format sources as a formal bibliography for clinical reports.
    
    Args:
        sources: List of source metadata dictionaries
        
    Returns:
        Formatted bibliography string
    """
    if not sources:
        return ""
    
    # Separate by source type
    local_sources = [s for s in sources if s.get("source_type") == "Local"]
    national_sources = [s for s in sources if s.get("source_type") == "National"]
    other_sources = [
        s for s in sources 
        if s.get("source_type") not in ["Local", "National"]
    ]
    
    bibliography_lines = ["**Bibliography**\n"]
    
    # Format Local Authority sources
    if local_sources:
        bibliography_lines.append("**Local Authority:**")
        for source in local_sources:
            org = source.get("organization", "Unknown")
            year = source.get("year", "")
            doc_name = source.get("file_name", "Unknown")
            clinical_area = source.get("clinical_area", "")
            
            # Clean document name (remove extension, clean up)
            doc_name_clean = doc_name.replace(".pdf", "").replace(".docx", "").replace("_", " ")
            
            if year:
                bibliography_lines.append(f"- {org} ({year}). {doc_name_clean}. {clinical_area}.")
            else:
                bibliography_lines.append(f"- {org}. {doc_name_clean}. {clinical_area}.")
        bibliography_lines.append("")
    
    # Format National Guidelines sources
    if national_sources:
        bibliography_lines.append("**National Guidelines:**")
        for source in national_sources:
            org = source.get("organization", "Unknown")
            year = source.get("year", "")
            ref_code = source.get("reference_code", "")
            doc_name = source.get("file_name", "Unknown")
            
            # Clean document name
            doc_name_clean = doc_name.replace(".pdf", "").replace(".docx", "").replace("_", " ")
            
            if ref_code:
                bibliography_lines.append(f"- {org} ({year if year else 'n.d.'}). {doc_name_clean}. {ref_code}.")
            elif year:
                bibliography_lines.append(f"- {org} ({year}). {doc_name_clean}.")
            else:
                bibliography_lines.append(f"- {org}. {doc_name_clean}.")
        bibliography_lines.append("")
    
    # Format other sources (Legal, Governance)
    if other_sources:
        bibliography_lines.append("**Other Sources:**")
        for source in other_sources:
            org = source.get("organization", "Unknown")
            year = source.get("year", "")
            doc_name = source.get("file_name", "Unknown")
            source_type = source.get("source_type", "")
            
            doc_name_clean = doc_name.replace(".pdf", "").replace(".docx", "").replace("_", " ")
            
            if year:
                bibliography_lines.append(f"- {org} ({year}). {doc_name_clean}. [{source_type}].")
            else:
                bibliography_lines.append(f"- {org}. {doc_name_clean}. [{source_type}].")
        bibliography_lines.append("")
    
    return "\n".join(bibliography_lines)


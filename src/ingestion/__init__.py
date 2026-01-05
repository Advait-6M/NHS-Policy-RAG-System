"""NEPPA Data Ingestion Module.

This module handles parsing of PDF and DOCX documents with metadata tagging
for the NHS Expert Patient Policy Assistant (NEPPA) system.
"""

from src.ingestion.parser import DocumentParser, DocumentMetadata

__all__ = ["DocumentParser", "DocumentMetadata"]


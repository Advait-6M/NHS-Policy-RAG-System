"""Test script for Sprint 1: Data Ingestion.

This script verifies that all raw documents are correctly detected and tagged
with appropriate metadata.
"""

import sys
from pathlib import Path

# Add src to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.ingestion.parser import DocumentParser

def main():
    """Run ingestion test and display results."""
    print("=" * 70)
    print("NEPPA Sprint 1: Data Ingestion Test")
    print("=" * 70)
    print()

    # Initialize parser
    data_root = project_root / "data" / "raw"
    parser = DocumentParser(data_root)

    # Discover documents
    print(f"Scanning for documents in: {data_root}")
    documents = parser.discover_documents()
    print(f"Found {len(documents)} documents\n")

    if not documents:
        print("ERROR: No documents found. Please verify files are in data/raw/")
        return 1

    # Display document list
    print("Discovered Documents:")
    print("-" * 70)
    for idx, doc_path in enumerate(documents, 1):
        relative_path = doc_path.relative_to(data_root)
        print(f"{idx:2d}. {relative_path}")

    print()
    print("=" * 70)
    print("Testing Metadata Inference")
    print("=" * 70)
    print()

    # Test metadata inference for each document
    metadata_results = []
    for doc_path in documents:
        try:
            metadata = parser._infer_metadata_from_path(doc_path)
            metadata_results.append((doc_path, metadata))

            print(f"File: {doc_path.name}")
            print(f"  Source Type: {metadata.source_type}")
            print(f"  Organization: {metadata.organization}")
            print(f"  Clinical Area: {metadata.clinical_area}")
            print(f"  Last Updated: {metadata.last_updated or 'N/A'}")
            print()

        except Exception as e:
            print(f"ERROR processing {doc_path.name}: {e}")
            print()

    # Summary statistics
    print("=" * 70)
    print("Summary Statistics")
    print("=" * 70)
    print()

    source_type_counts = {}
    organization_counts = {}
    clinical_area_counts = {}

    for _, metadata in metadata_results:
        source_type_counts[metadata.source_type] = source_type_counts.get(
            metadata.source_type, 0
        ) + 1
        organization_counts[metadata.organization] = organization_counts.get(
            metadata.organization, 0
        ) + 1
        clinical_area_counts[metadata.clinical_area] = clinical_area_counts.get(
            metadata.clinical_area, 0
        ) + 1

    print("Documents by Source Type:")
    for source_type, count in sorted(source_type_counts.items()):
        print(f"  {source_type}: {count}")

    print()
    print("Documents by Organization:")
    for org, count in sorted(organization_counts.items()):
        print(f"  {org}: {count}")

    print()
    print("Documents by Clinical Area:")
    for area, count in sorted(clinical_area_counts.items()):
        print(f"  {area}: {count}")

    print()
    print("=" * 70)
    print("Testing Full Parsing (first 3 documents only)")
    print("=" * 70)
    print()

    # Test parsing on first 3 documents
    parse_success = 0
    parse_failed = 0

    for doc_path in documents[:3]:
        try:
            print(f"Parsing: {doc_path.name}...", end=" ")
            if doc_path.suffix.lower() == ".pdf":
                text, metadata = parser.parse_pdf(doc_path)
            elif doc_path.suffix.lower() == ".docx":
                text, metadata = parser.parse_docx(doc_path)
            else:
                print("SKIPPED (unsupported format)")
                continue

            char_count = len(text)
            word_count = len(text.split())
            print(f"SUCCESS ({char_count:,} chars, {word_count:,} words)")

            parse_success += 1

        except Exception as e:
            print(f"FAILED: {e}")
            parse_failed += 1

    print()
    print("=" * 70)
    if parse_success > 0:
        print(f"[SUCCESS] Parsing test completed: {parse_success} succeeded, {parse_failed} failed")
    else:
        print(f"[FAILED] Parsing test failed: {parse_failed} errors")
    print("=" * 70)

    return 0 if parse_success > 0 else 1

if __name__ == "__main__":
    sys.exit(main())


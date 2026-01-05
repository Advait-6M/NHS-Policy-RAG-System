"""Run full ingestion pipeline for Sprint 1.

This script parses all documents and saves the results to data/processed/.
"""

import sys
from pathlib import Path

# Add src to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.ingestion.parser import DocumentParser

def main():
    """Run the full ingestion pipeline."""
    print("=" * 70)
    print("NEPPA Sprint 1: Full Document Ingestion")
    print("=" * 70)
    print()

    # Initialize parser
    data_root = project_root / "data" / "raw"
    output_dir = project_root / "data" / "processed"
    
    parser = DocumentParser(data_root)

    # Parse all documents with chunking
    print(f"Parsing documents from: {data_root}")
    print(f"Output directory: {output_dir}")
    print(f"Chunk size: 1000 characters (with 200 char overlap)")
    print()

    chunks = parser.parse_all(output_dir=output_dir, chunk_size=1000, overlap=200)

    # Display summary
    print()
    print("=" * 70)
    print("Ingestion Summary")
    print("=" * 70)
    print()

    # Count unique documents (by file_name)
    unique_docs = set()
    source_type_counts = {}
    clinical_area_counts = {}
    chunks_with_headers = 0
    total_chars = 0
    total_words = 0

    for chunk in chunks:
        metadata = chunk["metadata"]
        file_name = metadata["file_name"]
        unique_docs.add(file_name)
        
        source_type = metadata["source_type"]
        source_type_counts[source_type] = source_type_counts.get(source_type, 0) + 1
        
        clinical_area = metadata.get("clinical_area", "Unknown")
        clinical_area_counts[clinical_area] = clinical_area_counts.get(clinical_area, 0) + 1
        
        if metadata.get("context_header"):
            chunks_with_headers += 1
        
        text = chunk["text"]
        total_chars += len(text)
        total_words += len(text.split())

    print(f"Total documents processed: {len(unique_docs)}")
    print(f"Total chunks created: {len(chunks)}")
    print(f"Chunks with context headers: {chunks_with_headers} ({chunks_with_headers/len(chunks)*100:.1f}%)")
    print()

    print("Chunks by Source Type:")
    for source_type, count in sorted(source_type_counts.items()):
        print(f"  {source_type}: {count}")

    print()
    print("Chunks by Clinical Area:")
    for area, count in sorted(clinical_area_counts.items()):
        print(f"  {area}: {count}")

    print()
    print(f"Total text extracted: {total_chars:,} characters, {total_words:,} words")
    print(f"Average chunk size: {total_chars//len(chunks) if chunks else 0:,} characters")
    print()

    print("Processed files saved to:", output_dir)
    print(f"Generated chunk files for {len(unique_docs)} documents")
    print()
    print("=" * 70)
    print("[SUCCESS] Ingestion completed successfully!")
    print("=" * 70)

    return 0

if __name__ == "__main__":
    sys.exit(main())


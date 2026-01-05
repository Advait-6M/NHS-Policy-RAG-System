"""Review and verify metadata assignments in chunk JSON files.

This script reviews all chunk files and verifies source_type and clinical_area assignments.
It also generates an ingestion_summary.json file.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

def main():
    """Review all chunk JSON files and verify metadata."""
    project_root = Path(__file__).parent.parent
    processed_dir = project_root / "data" / "processed"
    
    if not processed_dir.exists():
        print(f"ERROR: Processed directory not found: {processed_dir}")
        return 1
    
    # Get all chunk files (not the _parsed.json files)
    chunk_files = list(processed_dir.glob("*_chunks.json"))
    
    if not chunk_files:
        print("No chunk JSON files found in processed directory")
        return 1
    
    print("=" * 70)
    print("Chunk Metadata Review - All Documents")
    print("=" * 70)
    print()
    
    issues = []
    source_type_counts = defaultdict(int)
    clinical_area_counts = defaultdict(int)
    organization_counts = defaultdict(int)
    context_header_counts = defaultdict(int)
    total_chunks = 0
    chunks_with_headers = 0
    chunks_without_headers = 0
    
    all_chunks_summary = []
    
    for chunk_file in sorted(chunk_files):
        try:
            with open(chunk_file, "r", encoding="utf-8") as f:
                chunks = json.load(f)
            
            # Handle both single object and array formats
            if not isinstance(chunks, list):
                chunks = [chunks]
            
            file_issues = []
            file_chunks_with_headers = 0
            file_chunks_without_headers = 0
            
            for chunk_idx, chunk in enumerate(chunks):
                total_chunks += 1
                metadata = chunk.get("metadata", {})
                file_name = metadata.get("file_name", chunk_file.name)
                source_type = metadata.get("source_type", "MISSING")
                clinical_area = metadata.get("clinical_area", "MISSING")
                organization = metadata.get("organization", "MISSING")
                context_header = metadata.get("context_header")
                
                # Track counts
                source_type_counts[source_type] += 1
                clinical_area_counts[clinical_area] += 1
                organization_counts[organization] += 1
                
                if context_header:
                    chunks_with_headers += 1
                    file_chunks_with_headers += 1
                    context_header_counts[context_header[:50]] += 1  # Track first 50 chars
                else:
                    chunks_without_headers += 1
                    file_chunks_without_headers += 1
                
                # Check for issues
                chunk_issues = []
                if source_type == "MISSING":
                    chunk_issues.append("Missing source_type")
                if clinical_area == "MISSING":
                    chunk_issues.append("Missing clinical_area")
                if organization == "MISSING":
                    chunk_issues.append("Missing organization")
                
                # Verify source_type matches file path
                file_path = metadata.get("file_path", "")
                if "01_National" in file_path and source_type != "National":
                    chunk_issues.append(f"Path suggests National but source_type is {source_type}")
                elif "02_Local" in file_path and source_type != "Local":
                    chunk_issues.append(f"Path suggests Local but source_type is {source_type}")
                elif "03_Governance" in file_path and source_type != "Governance":
                    chunk_issues.append(f"Path suggests Governance but source_type is {source_type}")
                elif "04_IFR_process" in file_path and source_type != "Legal":
                    chunk_issues.append(f"Path suggests Legal but source_type is {source_type}")
                
                # Verify clinical_area matches content
                if "diabetes" in file_name.lower() and clinical_area != "Diabetes":
                    chunk_issues.append(f"Filename suggests Diabetes but clinical_area is {clinical_area}")
                
                if chunk_issues:
                    file_issues.append(f"Chunk {chunk_idx + 1}: {', '.join(chunk_issues)}")
            
            # Store summary for this file
            all_chunks_summary.append({
                "file_name": file_name,
                "total_chunks": len(chunks),
                "chunks_with_headers": file_chunks_with_headers,
                "chunks_without_headers": file_chunks_without_headers,
                "source_type": metadata.get("source_type"),
                "organization": metadata.get("organization"),
                "clinical_area": metadata.get("clinical_area"),
                "issues": file_issues
            })
            
            # Display file summary
            status = "[OK]" if not file_issues else "[ISSUE]"
            print(f"{status} {file_name}")
            print(f"   Total Chunks: {len(chunks)}")
            print(f"   Chunks with Context Headers: {file_chunks_with_headers} ({file_chunks_with_headers/len(chunks)*100:.1f}%)")
            print(f"   Source Type: {metadata.get('source_type')}")
            print(f"   Organization: {metadata.get('organization')}")
            print(f"   Clinical Area: {metadata.get('clinical_area')}")
            if file_issues:
                print(f"   ISSUES: {len(file_issues)} chunk(s) with problems")
                for issue in file_issues[:3]:  # Show first 3 issues
                    print(f"     - {issue}")
                if len(file_issues) > 3:
                    print(f"     ... and {len(file_issues) - 3} more")
            print()
            
            if file_issues:
                issues.append((file_name, file_issues))
            
        except Exception as e:
            print(f"ERROR processing {chunk_file.name}: {e}")
            issues.append((chunk_file.name, [f"Parse error: {e}"]))
            print()
    
    # Create ingestion summary
    summary = {
        "total_documents": len(chunk_files),
        "total_chunks": total_chunks,
        "chunks_with_context_headers": chunks_with_headers,
        "chunks_without_context_headers": chunks_without_headers,
        "context_header_coverage": f"{(chunks_with_headers/total_chunks*100):.1f}%" if total_chunks > 0 else "0%",
        "source_type_distribution": dict(source_type_counts),
        "clinical_area_distribution": dict(clinical_area_counts),
        "organization_distribution": dict(organization_counts),
        "document_summary": all_chunks_summary,
        "issues_found": len(issues)
    }
    
    # Save ingestion summary
    summary_file = processed_dir / "ingestion_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"Saved ingestion summary to: {summary_file}")
    print()
    
    # Display summary statistics
    print("=" * 70)
    print("Summary Statistics")
    print("=" * 70)
    print()
    print(f"Total Documents: {len(chunk_files)}")
    print(f"Total Chunks: {total_chunks}")
    print(f"Chunks with Context Headers: {chunks_with_headers} ({chunks_with_headers/total_chunks*100:.1f}%)")
    print(f"Chunks without Context Headers: {chunks_without_headers} ({chunks_without_headers/total_chunks*100:.1f}%)")
    print()
    print("Source Types:")
    for st, count in sorted(source_type_counts.items()):
        print(f"  {st}: {count} chunks")
    print()
    print("Clinical Areas:")
    for ca, count in sorted(clinical_area_counts.items()):
        print(f"  {ca}: {count} chunks")
    print()
    print("Organizations:")
    for org, count in sorted(organization_counts.items()):
        print(f"  {org}: {count} chunks")
    print()
    
    if issues:
        print("=" * 70)
        print(f"ISSUES FOUND: {len(issues)} files with problems")
        print("=" * 70)
        for file_name, file_issues in issues[:10]:  # Show first 10
            print(f"{file_name}: {len(file_issues)} issue(s)")
        if len(issues) > 10:
            print(f"... and {len(issues) - 10} more files with issues")
        return 1
    else:
        print("=" * 70)
        print("[SUCCESS] All metadata assignments verified successfully!")
        print("=" * 70)
        return 0

if __name__ == "__main__":
    sys.exit(main())


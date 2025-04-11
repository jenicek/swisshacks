#!/usr/bin/env python
"""
Command-line script to extract text from PDF files, with special support for
account opening forms and financial documents.

Usage:
    python extract_pdf_text.py path/to/document.pdf [--metadata] [--forms] [--account-info] [--tables] [--output output.txt]
"""

import argparse
import os
import sys
import json
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from data_parsing.parse_pdf import (
    extract_text_from_pdf,
    extract_pdf_metadata,
    extract_form_fields,
    extract_tables_from_pdf
)


def main():
    parser = argparse.ArgumentParser(description="Extract text and data from PDF files")
    parser.add_argument("file", help="Path to the PDF file")
    parser.add_argument("--metadata", "-m", action="store_true", help="Extract metadata")
    parser.add_argument("--forms", "-f", action="store_true", help="Extract form fields (if available)")
    parser.add_argument("--tables", "-t", action="store_true", help="Extract tables from the PDF")
    parser.add_argument("--password", "-p", help="Password for encrypted PDF")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    parser.add_argument("--json", "-j", action="store_true", help="Output in JSON format")
    args = parser.parse_args()

    # Check if file exists
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File '{args.file}' does not exist", file=sys.stderr)
        sys.exit(1)
    
    # Check if it's a PDF file
    if not file_path.suffix.lower() == '.pdf':
        print(f"Error: File '{args.file}' is not a PDF file", file=sys.stderr)
        sys.exit(1)

    try:
        # Read the file
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Create a dictionary to store all the results
        results = {}
        
        # Extract text
        text = extract_text_from_pdf(content, password=args.password)
        results["text"] = text
        
        # Extract metadata if requested
        if args.metadata:
            try:
                metadata = extract_pdf_metadata(content)
                results["metadata"] = metadata
            except Exception as e:
                print(f"Warning: Could not extract metadata: {e}", file=sys.stderr)
        
        # Extract form fields if requested
        if args.forms:
            try:
                form_fields = extract_form_fields(content)
                if form_fields:
                    results["form_fields"] = form_fields
                else:
                    print("No form fields found in the PDF", file=sys.stderr)
            except Exception as e:
                print(f"Warning: Could not extract form fields: {e}", file=sys.stderr)
        
        # Extract tables if requested
        if args.tables:
            try:
                tables = extract_tables_from_pdf(content)
                if tables:
                    results["tables"] = [table for table in tables]
                else:
                    print("No tables found in the PDF", file=sys.stderr)
            except Exception as e:
                print(f"Warning: Could not extract tables: {e}", file=sys.stderr)
                
        # Output results
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                if args.json:
                    json.dump(results, f, indent=2, default=str)
                else:
                    f.write(text)
                    
                    if args.metadata and "metadata" in results:
                        f.write("\n\n===== Document Metadata =====\n")
                        for key, value in results["metadata"].items():
                            f.write(f"{key}: {value}\n")
                    
                    if args.forms and "form_fields" in results:
                        f.write("\n\n===== Form Fields =====\n")
                        for key, value in results["form_fields"].items():
                            f.write(f"{key}: {value}\n")
                    
                    if args.account_info and "account_info" in results:
                        f.write("\n\n===== Account Information =====\n")
                        for key, value in results["account_info"].items():
                            f.write(f"{key}: {value}\n")
                    
                    if args.tables and "tables" in results:
                        f.write("\n\n===== Tables =====\n")
                        for i, table in enumerate(results["tables"]):
                            f.write(f"\nTable {i+1}:\n")
                            for row in table:
                                f.write(" | ".join(row) + "\n")
                    
            print(f"Output written to: {args.output}")
        else:
            # Print to stdout
            if args.json:
                print(json.dumps(results, indent=2, default=str))
            else:
                print("\n===== Document Content =====")
                print(text)
                
                if args.metadata and "metadata" in results:
                    print("\n===== Document Metadata =====")
                    for key, value in results["metadata"].items():
                        print(f"{key}: {value}")
                
                if args.forms and "form_fields" in results:
                    print("\n===== Form Fields =====")
                    for key, value in results["form_fields"].items():
                        print(f"{key}: {value}")
                
                if args.account_info and "account_info" in results:
                    print("\n===== Account Information =====")
                    for key, value in results["account_info"].items():
                        print(f"{key}: {value}")
                
                if args.tables and "tables" in results:
                    print("\n===== Tables =====")
                    for i, table in enumerate(results["tables"]):
                        print(f"\nTable {i+1}:")
                        for row in table:
                            print(" | ".join(row))
            
        return 0
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
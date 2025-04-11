#!/usr/bin/env python
"""
Command-line script to extract text from DOCX files.

Usage:
    python extract_docx_text.py path/to/document.docx [--metadata] [--output output.txt]
"""

import argparse
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from data_parsing.parse_docx import extract_text_from_docx, extract_document_metadata


def main():
    parser = argparse.ArgumentParser(description="Extract text from DOCX files")
    parser.add_argument("file", help="Path to the DOCX file")
    parser.add_argument("--metadata", "-m", action="store_true", help="Extract metadata")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    args = parser.parse_args()

    # Check if file exists
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File '{args.file}' does not exist", file=sys.stderr)
        sys.exit(1)
    
    # Check if it's a docx file
    if not file_path.suffix.lower() == '.docx':
        print(f"Error: File '{args.file}' is not a DOCX file", file=sys.stderr)
        sys.exit(1)

    try:
        # Read the file
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Extract text
        text = extract_text_from_docx(content)
        
        # Extract metadata if requested
        if args.metadata:
            metadata = extract_document_metadata(content)
            
            # Print basic stats
            print("\n===== Document Statistics =====")
            print(f"Character count: {len(text)}")
            print(f"Word count: {len(text.split())}")
            print(f"Line count: {len(text.splitlines())}")
            
            # Print metadata
            print("\n===== Document Metadata =====")
            for key, value in metadata.items():
                print(f"{key}: {value}")
        
        # Output text content
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"Text extracted to: {args.output}")
        else:
            print("\n===== Document Content =====")
            print(text)
            
        return 0
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
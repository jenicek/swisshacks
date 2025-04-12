#!/usr/bin/env python3
"""
Script to parse banking forms from PDF and save cleaned form field data as JSON.
Handles form field extraction, cleaning, and signature detection.
"""

import json
import os
import argparse
from pathlib import Path
from data_parsing.parse_pdf import extract_form_fields, extract_text_from_pdf
import re
from io import BytesIO


def parse_banking_form(pdf_path: Path) -> dict:
    """
    Parse a banking form PDF and extract cleaned form fields.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        dict: Cleaned form field data
    """
    # Read the PDF file
    with open(pdf_path, "rb") as file:
        return parse_banking_pdf(file.read())


def parse_banking_pdf(data: bytes):
    """
    Parse banking form PDF data and extract cleaned form fields.

    Args:
        data: PDF file content as bytes

    Returns:
        dict: Cleaned form field data
    """
    # Use BytesIO to create a file-like object from the bytes data
    pdf_file = BytesIO(data)

    # Extract form fields with clean_output=True for simplified output
    form_data = extract_form_fields(pdf_file, clean_output=True)

    # If we couldn't detect a signature in the form fields, try text-based detection
    if "_signature_fields" not in form_data:
        # Reset the file pointer to the beginning
        pdf_file.seek(0)

        # Extract text from the PDF to look for signature sections
        text = extract_text_from_pdf(pdf_file)

        # Look for common signature section indicators in the text
        signature_patterns = [
            r"(?i)specimen\s+signature",
            r"(?i)signature\s+specimen",
            r"(?i)signature\s+of\s+applicant",
            r"(?i)customer\s+signature",
            r"(?i)sign\s+here",
        ]

        for pattern in signature_patterns:
            if re.search(pattern, text):
                form_data["_signature_fields"] = {"specimen_signature": True}
                break

    return form_data



def save_form_data_as_json(form_data: dict, output_path: str = None) -> str:
    """
    Save form data to a JSON file.

    Args:
        form_data: The extracted form field data
        output_path: Path where to save the JSON file (optional)

    Returns:
        str: Path to the saved JSON file
    """
    if not output_path:
        output_path = "form_data.json"

    # Ensure the directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    # Save the data to JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(form_data, f, indent=2, ensure_ascii=False)

    return output_path


def main() -> int:
    """Main function to parse command line arguments and process PDF forms."""
    parser = argparse.ArgumentParser(
        description="Parse banking forms from PDF and save as JSON"
    )
    parser.add_argument("pdf_path", help="Path to the PDF form file")
    parser.add_argument(
        "-o", "--output", help="Output JSON file path (default: form_data.json)"
    )

    args = parser.parse_args()

    try:
        # Parse the banking form
        print(f"Parsing form fields from {args.pdf_path}...")
        form_data = parse_banking_form(args.pdf_path)

        # Save the form data to JSON
        output_path = args.output or "form_data.json"
        save_path = save_form_data_as_json(form_data, output_path)

        # Report on signature fields if any
        if "_signature_fields" in form_data:
            print("\nSignature field status:")
            for field_name, has_signature in form_data["_signature_fields"].items():
                status = "SIGNED" if has_signature else "NOT SIGNED"
                print(f"  - {field_name}: {status}")
        else:
            print("\nNo signature fields detected in the document.")

        print(f"\nForm data extracted and saved to {save_path}")
        print(
            f"Total fields extracted: {len(form_data) - ('_signature_fields' in form_data)}"
        )

    except Exception as e:
        print(f"Error processing the form: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

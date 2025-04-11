"""
PDF parsing utilities for extracting text and form data from PDF documents.
Particularly useful for account opening forms and financial documents.
"""

import io
from typing import Union, BinaryIO, List, Dict, Any
import re

try:
    from PyPDF2 import PdfReader
except ImportError:
    raise ImportError("PyPDF2 package is required. Install it with: pip install PyPDF2")


def extract_text_from_pdf(file_content: Union[bytes, BinaryIO], 
                         password: str = None) -> str:
    """
    Extract text from a PDF file.
    
    Args:
        file_content: Either bytes content of the PDF or a file-like object
        password: Optional password if the PDF is encrypted
        
    Returns:
        str: The extracted text from the PDF
    """
    try:
        # If we get bytes, convert to file-like object
        if isinstance(file_content, bytes):
            file_content = io.BytesIO(file_content)
            
        # Create PDF reader object
        pdf = PdfReader(file_content)
        
        # If the PDF is encrypted and a password is provided, try to decrypt it
        if pdf.is_encrypted and password:
            pdf.decrypt(password)
            
        # Extract text from all pages
        text_content = []
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                text_content.append(text)
        
        return "\n\n".join(text_content)
    except Exception as e:
        raise ValueError(f"Error extracting text from PDF: {str(e)}")


def extract_pdf_metadata(file_content: Union[bytes, BinaryIO]) -> Dict[str, Any]:
    """
    Extract metadata from a PDF file.
    
    Args:
        file_content: Either bytes content of the PDF or a file-like object
        
    Returns:
        Dict: Document metadata including author, creation date, etc.
    """
    try:
        # If we get bytes, convert to file-like object
        if isinstance(file_content, bytes):
            file_content = io.BytesIO(file_content)
            
        pdf = PdfReader(file_content)
        
        # Extract metadata from info dictionary
        metadata = {}
        if pdf.metadata:
            for key, value in pdf.metadata.items():
                # Convert /Key format to regular key format
                clean_key = key.strip('/') if isinstance(key, str) else key
                metadata[clean_key] = value
                
        # Add other useful information
        metadata['Pages'] = len(pdf.pages)
        metadata['Encrypted'] = pdf.is_encrypted
        
        return metadata
    except Exception as e:
        raise ValueError(f"Error extracting metadata from PDF: {str(e)}")


def extract_form_fields(file_content: Union[bytes, BinaryIO], clean_output: bool = True) -> Dict[str, Any]:
    """
    Extract form fields from a PDF file.
    Particularly useful for account opening forms and financial documents.
    
    Args:
        file_content: Either bytes content of the PDF or a file-like object
        clean_output: If True, returns only field names and values (simplified format)
                     If False, returns the raw field data
        
    Returns:
        Dict: Form field names and their values
    """
    try:
        # If we get bytes, convert to file-like object
        if isinstance(file_content, bytes):
            file_content = io.BytesIO(file_content)
            
        pdf = PdfReader(file_content)
        
        # Get form fields if they exist
        form_data = {}
        raw_fields = pdf.get_fields() or {}
        
        if clean_output:
            # Process and clean form fields
            for field_name, field_data in raw_fields.items():
                # Extract the actual field name from the '/T' key
                name = field_data.get('/T', field_name).strip('/')
                
                # Extract the value based on field type
                field_type = field_data.get('/FT')
                
                # Handle different field types
                if field_type == '/Tx':  # Text field
                    value = field_data.get('/V', '')
                    if isinstance(value, str):
                        value = value.strip('/')
                elif field_type == '/Btn':  # Button (checkbox, radio)
                    value = field_data.get('/V', '') == '/Yes'
                elif field_type == '/Sig':  # Signature field
                    # Check if the signature field has content
                    if '/V' in field_data and field_data['/V'] is not None:
                        value = True  # Signature exists
                    else:
                        value = False  # No signature
                else:
                    # For other field types, just get the raw value
                    value = field_data.get('/V', '')
                    if isinstance(value, str):
                        value = value.strip('/')
                
                form_data[name] = value
        else:
            # Return raw field data
            form_data = raw_fields
            
        # Check for signature fields specifically
        signature_fields = {}
        for field_name, field_data in raw_fields.items():
            if field_data.get('/FT') == '/Sig':
                name = field_data.get('/T', field_name).strip('/')
                has_signature = '/V' in field_data and field_data['/V'] is not None
                signature_fields[name] = has_signature
                
        # Check for embedded signatures (not form fields)
        embedded_signature_found = False
        signature_section_patterns = [
            r'(?i)specimen\s+signature',
            r'(?i)signature\s+specimen',
            r'(?i)signature\s+of\s+applicant',
            r'(?i)customer\s+signature'
        ]
        
        # Check text content for signature sections
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            
            # Look for signature section patterns in the text
            for pattern in signature_section_patterns:
                if re.search(pattern, text):
                    # If we find a signature section, check for images or XObject references
                    if "/Resources" in page and "/XObject" in page["/Resources"]:
                        # XObject can be images or other embedded objects
                        embedded_signature_found = True
                        break
                        
            if embedded_signature_found:
                break
        
        # Add embedded signature detection to the output
        if embedded_signature_found:
            signature_fields['specimen_signature'] = True
            
        if signature_fields:
            form_data['_signature_fields'] = signature_fields
            
        # Check for form fields related to signatures even if they're not signature type fields
        for field_name, value in form_data.items():
            if ('signature' in field_name.lower() or 'sign' in field_name.lower()) and value:
                if '_signature_fields' not in form_data:
                    form_data['_signature_fields'] = {}
                form_data['_signature_fields'][field_name] = True
            
        return form_data
    except Exception as e:
        raise ValueError(f"Error extracting form fields from PDF: {str(e)}")

def extract_tables_from_pdf(file_content: Union[bytes, BinaryIO]) -> List[List[str]]:
    """
    Extract simple tabular data from a PDF.
    This is a basic implementation that looks for consistent spacing patterns.
    For complex tables, consider using specialized libraries like tabula-py or camelot.
    
    Args:
        file_content: Either bytes content of the PDF or a file-like object
        
    Returns:
        List: List of extracted table rows (as lists of strings)
    """
    # Simple table extraction based on spacing patterns
    # This is a basic implementation that may not work for all PDFs
    
    # Extract text
    text = extract_text_from_pdf(file_content)
    lines = text.split('\n')
    
    # Look for table-like structures (lines with consistent spacing/tabbing)
    tables = []
    current_table = []
    
    for line in lines:
        # Skip empty lines
        if not line.strip():
            if current_table:
                tables.append(current_table)
                current_table = []
            continue
            
        # Check if line might be part of a table (contains multiple whitespace-separated values)
        parts = [p for p in re.split(r'\s{2,}', line) if p.strip()]
        if len(parts) >= 3:  # Assume it's a table row if it has at least 3 columns
            current_table.append(parts)
        else:
            if current_table and len(current_table) > 2:  # Save the table if it has at least 3 rows
                tables.append(current_table)
            current_table = []
    
    # Add the last table if it exists
    if current_table and len(current_table) > 2:
        tables.append(current_table)
        
    return tables
"""
PDF parsing utilities for extracting text and form data from PDF documents.
Particularly useful for account opening forms and financial documents.
"""

import io
from typing import Union, BinaryIO, List, Dict, Any, Optional, Tuple
from datetime import datetime
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


def extract_form_fields(file_content: Union[bytes, BinaryIO]) -> Dict[str, Any]:
    """
    Extract form fields from a PDF file.
    Particularly useful for account opening forms and financial documents.
    
    Args:
        file_content: Either bytes content of the PDF or a file-like object
        
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
        if pdf.get_fields():
            form_data = pdf.get_fields()
            
        return form_data
    except Exception as e:
        raise ValueError(f"Error extracting form fields from PDF: {str(e)}")


def find_account_information(text: str) -> Dict[str, Any]:
    """
    Parse extracted text to find common account opening information.
    Uses regex patterns to identify common fields in financial forms.
    
    Args:
        text: The extracted text from the PDF
        
    Returns:
        Dict: Extracted account information
    """
    account_info = {}
    
    # Define regex patterns for common account fields
    patterns = {
        'account_number': r'(?:Account|Acct)(?:\s+|\.)(?:No|Number|#|Num)(?:\.|\:|\s*)\s*([A-Z0-9]{4,20})',
        'name': r'(?:Name|Full Name|Customer Name)(?:\.|\:|\s*)\s*([A-Za-z\s\.]{5,50})',
        'date_of_birth': r'(?:Date of Birth|DOB|Birth Date)(?:\.|\:|\s*)\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
        'address': r'(?:Address|Residential Address|Home Address)(?:\.|\:|\s*)\s*([A-Za-z0-9\s\.,#\-]{10,100})',
        'phone': r'(?:Phone|Telephone|Mobile|Cell)(?:\.|\:|\s*)\s*((?:\+\d{1,3}[\s\-\.])?\(?\d{3}\)?[\s\-\.]?\d{3}[\s\-\.]?\d{4})',
        'email': r'(?:Email|E-mail)(?:\.|\:|\s*)\s*([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})',
        'tax_id': r'(?:SSN|Tax ID|TIN|Social Security)(?:\.|\:|\s*)\s*(\d{3}[\s\-]?\d{2}[\s\-]?\d{4})',
    }
    
    # Extract information using the patterns
    for field, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            account_info[field] = match.group(1).strip()
    
    return account_info


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
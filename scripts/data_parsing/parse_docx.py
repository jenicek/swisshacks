"""
Document processing utilities for extracting text from various document formats.
"""

import io
from typing import Union, BinaryIO, Dict, Any

from docx import Document


def extract_text_from_docx(file_content: Union[bytes, BinaryIO]) -> str:
    """
    Extract plain text from a .docx file.
    
    Args:
        file_content: Either bytes content of the document or a file-like object
        
    Returns:
        str: The extracted text from the document
    """
    try:
        # If we get bytes, convert to file-like object
        if isinstance(file_content, bytes):
            file_content = io.BytesIO(file_content)
            
        doc = Document(file_content)
        
        # Extract text from paragraphs
        full_text = []
        for para in doc.paragraphs:
            if para.text.strip():  # Skip empty paragraphs
                full_text.append(para.text)
        
        # Extract text from tables
        for table in doc.tables:
            for row in table.rows:
                row_text = []
                for cell in row.cells:
                    if cell.text.strip():  # Skip empty cells
                        row_text.append(cell.text.strip())
                if row_text:  # Skip empty rows
                    full_text.append(" | ".join(row_text))
        
        return "\n".join(full_text)
    except Exception as e:
        raise ValueError(f"Error extracting text from DOCX: {str(e)}")


def extract_document_metadata(file_content: Union[bytes, BinaryIO]) -> Dict[str, Any]:
    """
    Extract metadata from a .docx file.
    
    Args:
        file_content: Either bytes content of the document or a file-like object
        
    Returns:
        Dict: Document metadata including author, created date, etc.
    """
    try:
        # If we get bytes, convert to file-like object
        if isinstance(file_content, bytes):
            file_content = io.BytesIO(file_content)
            
        doc = Document(file_content)
        
        # Extract core properties
        core_props = doc.core_properties
        
        metadata = {
            "author": core_props.author,
            "created": core_props.created,
            "last_modified_by": core_props.last_modified_by,
            "last_modified": core_props.modified,
            "title": core_props.title,
            "subject": core_props.subject,
            "keywords": core_props.keywords,
            "comments": core_props.comments,
            "category": core_props.category,
            "language": core_props.language,
            "revision": core_props.revision,
        }
        
        # Filter out None values
        metadata = {k: v for k, v in metadata.items() if v is not None}
        
        return metadata
    except Exception as e:
        raise ValueError(f"Error extracting metadata from DOCX: {str(e)}")
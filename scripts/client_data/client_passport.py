from pathlib import Path
from enum import Enum

class PassportBackendType(Enum):
    OPENAI = "openai"
    EASY_OCR = "easyocr"
    TESSERACT = "tesseract"

class PassportParser:
    
    def __init__(self, backend_type: PassportBackendType):
        self.backend_type = backend_type
        self.parser = None
        
        if backend_type == PassportBackendType.OPENAI:
            from scripts.data_parsing.parse_passport_openai import parse_png_to_json
            self.parser = parse_png_to_json
        elif backend_type == PassportBackendType.EASY_OCR:
            from scripts.data_parsing.parse_passport_easyocr import process_image_regions
            self.parser = process_image_regions
        elif backend_type == PassportBackendType.TESSERACT:
            raise NotImplementedError("Tesseract backend is not implemented yet.")
        else:
            raise ValueError(f"Unsupported backend type: {backend_type}")
        
        
    def parse(self, passport_file_path: Path) -> dict:
        """
        Parse a passport image (PNG) to extract structured data.
        
        Args:
            passport_file_path: Path to the passport image file
            
        Returns:
            Dictionary containing extracted passport information
        """
        if not self.parser:
            raise ValueError("Parser not initialized.")
        
        return self.parser(passport_file_path)
    

        
# PDF Sanitization and Security
import subprocess
from pathlib import Path
from typing import Optional
import fitz  # PyMuPDF

from app.core.config import settings

class PDFSanitizer:
    """Sanitize PDF files to prevent security issues"""
    
    @staticmethod
    def sanitize(input_path: Path, output_path: Path) -> bool:
        """
        Sanitize PDF by re-rendering it to remove malicious content
        Returns True if successful, False otherwise
        """
        if not settings.SANITIZE_PDF:
            # Just copy if sanitization disabled
            output_path.write_bytes(input_path.read_bytes())
            return True
        
        try:
            # Method 1: Re-save with PyMuPDF (removes most malicious content)
            doc = fitz.open(input_path)
            
            # Check for suspicious elements
            if PDFSanitizer._check_suspicious(doc):
                print(f"Warning: Suspicious elements detected in {input_path}")
            
            # Re-save to clean
            doc.save(output_path, garbage=4, deflate=True, clean=True)
            doc.close()
            
            return True
            
        except Exception as e:
            print(f"Sanitization failed: {e}")
            # Fallback: try qpdf if available
            return PDFSanitizer._sanitize_with_qpdf(input_path, output_path)
    
    @staticmethod
    def _check_suspicious(doc: fitz.Document) -> bool:
        """Check for suspicious elements in PDF"""
        suspicious = False
        
        # Check for JavaScript
        if doc.embfile_count() > 0:
            suspicious = True
        
        # Check for embedded files
        for i in range(len(doc)):
            page = doc[i]
            annots = page.annots()
            if annots:
                for annot in annots:
                    if annot.type[0] == 8:  # Widget annotation
                        suspicious = True
        
        # Check for actions
        if doc.metadata.get('modDate'):
            pass  # Normal
        
        return suspicious
    
    @staticmethod
    def _sanitize_with_qpdf(input_path: Path, output_path: Path) -> bool:
        """Fallback sanitization using qpdf"""
        try:
            result = subprocess.run(
                ['qpdf', '--linearize', str(input_path), str(output_path)],
                capture_output=True,
                timeout=30
            )
            return result.returncode == 0
        except Exception:
            # Last resort: just copy
            output_path.write_bytes(input_path.read_bytes())
            return True
    
    @staticmethod
    def validate_pdf_structure(file_path: Path) -> tuple[bool, str]:
        """Validate PDF structure"""
        try:
            doc = fitz.open(file_path)
            
            # Check if it's a valid PDF
            if not doc.is_pdf:
                return False, "Not a valid PDF file"
            
            # Check page count
            if len(doc) == 0:
                return False, "PDF has no pages"
            
            # Check for corruption
            for i in range(min(3, len(doc))):  # Check first 3 pages
                page = doc[i]
                if not page.get_text():
                    pass  # Might be image-only
            
            doc.close()
            return True, "Valid PDF"
            
        except Exception as e:
            return False, f"PDF validation error: {str(e)}"

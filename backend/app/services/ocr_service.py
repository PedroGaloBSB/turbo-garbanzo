# OCR Service using Tesseract
import subprocess
from pathlib import Path
from typing import Optional, List
import fitz  # PyMuPDF
from PIL import Image
import io

from app.core.config import settings

class OCRService:
    """OCR service for extracting text from scanned PDFs"""
    
    def __init__(self):
        self.enabled = settings.OCR_ENABLED
        self.languages = settings.OCR_LANGUAGES.split(',')
    
    def extract_text(self, pdf_path: Path) -> tuple[str, bool]:
        """
        Extract text from PDF using OCR if needed
        Returns: (text, used_ocr)
        """
        if not self.enabled:
            return self._extract_text_only(pdf_path), False
        
        try:
            doc = fitz.open(pdf_path)
            
            # First try to extract text normally
            text_parts = []
            needs_ocr = False
            
            for page in doc:
                text = page.get_text()
                if text.strip():
                    text_parts.append(text)
                else:
                    needs_ocr = True
                    # Render page as image and OCR
                    ocr_text = self._ocr_page(page)
                    if ocr_text:
                        text_parts.append(ocr_text)
            
            doc.close()
            
            text = "\n".join(text_parts)
            return text, needs_ocr
            
        except Exception as e:
            print(f"OCR extraction error: {e}")
            return self._extract_text_only(pdf_path), False
    
    def _extract_text_only(self, pdf_path: Path) -> str:
        """Extract text without OCR"""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception:
            return ""
    
    def _ocr_page(self, page: fitz.Page) -> str:
        """Perform OCR on a single page"""
        try:
            # Render page to image
            mat = fitz.Matrix(2, 2)  # 2x zoom for better quality
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            
            # Save temporarily
            temp_path = Path("/tmp/ocr_page.png")
            img.save(temp_path)
            
            # Run Tesseract
            result = subprocess.run(
                [
                    'tesseract',
                    str(temp_path),
                    'stdout',
                    '-l', '+'.join(self.languages)
                ],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Cleanup
            temp_path.unlink(missing_ok=True)
            
            if result.returncode == 0:
                return result.stdout
            else:
                print(f"Tesseract error: {result.stderr}")
                return ""
                
        except Exception as e:
            print(f"Page OCR error: {e}")
            return ""
    
    def is_available(self) -> bool:
        """Check if Tesseract is available"""
        if not self.enabled:
            return False
        
        try:
            result = subprocess.run(
                ['tesseract', '--version'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

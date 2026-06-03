"""
PDFForge - Pacote principal.
"""

from .core import PDFDocument, TextExtractor, ImageExtractor, DocumentCleaner
from .formats import ExportManager
from .utils import BatchProcessor, get_pdf_info, detect_pdf_type

__version__ = "0.1.0"
__author__ = "PDFForge Community"
__license__ = "MIT"

__all__ = [
    # Core
    "PDFDocument",
    "TextExtractor",
    "ImageExtractor", 
    "DocumentCleaner",
    
    # Formats
    "ExportManager",
    
    # Utils
    "BatchProcessor",
    "get_pdf_info",
    "detect_pdf_type",
]

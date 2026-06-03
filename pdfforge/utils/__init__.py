"""
PDFForge - Utilitários e funções auxiliares.
"""

from .helpers import detect_pdf_type, is_scanned_pdf, get_pdf_info
from .batch import BatchProcessor

__all__ = [
    "detect_pdf_type",
    "is_scanned_pdf",
    "get_pdf_info",
    "BatchProcessor",
]

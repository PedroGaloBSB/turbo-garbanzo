"""
PDFForge - Ferramenta de Manipulação de PDFs Open Source

Núcleo principal para leitura, processamento e manipulação de documentos PDF.
"""

from .document import PDFDocument
from .extractor import TextExtractor, ImageExtractor
from .cleaner import DocumentCleaner

__version__ = "0.1.0"
__author__ = "PDFForge Community"

__all__ = [
    "PDFDocument",
    "TextExtractor",
    "ImageExtractor",
    "DocumentCleaner",
]

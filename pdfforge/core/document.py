"""
Classe principal para representação e manipulação de documentos PDF.
"""

import fitz  # PyMuPDF
import pdfplumber
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
from .extractor import TextExtractor, ImageExtractor
from .cleaner import DocumentCleaner


class PDFDocument:
    """
    Classe principal para carregar, processar e manipular documentos PDF.
    
    Suporta PDFs baseados em texto, imagens, formulários e digitalizados.
    """
    
    def __init__(self, file_path: Union[str, Path]):
        """
        Inicializa um documento PDF.
        
        Args:
            file_path: Caminho para o arquivo PDF
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {self.file_path}")
        
        self._fitz_doc = None
        self._pdfplumber_doc = None
        self._metadata = None
        self._page_count = 0
        
    def _load_fitz(self):
        """Carrega o documento usando PyMuPDF (fitz)."""
        if self._fitz_doc is None:
            self._fitz_doc = fitz.open(self.file_path)
            self._page_count = len(self._fitz_doc)
            
    def _load_pdfplumber(self):
        """Carrega o documento usando pdfplumber."""
        if self._pdfplumber_doc is None:
            self._pdfplumber_doc = pdfplumber.open(self.file_path)
            
    @property
    def page_count(self) -> int:
        """Retorna o número de páginas do documento."""
        if self._page_count == 0:
            self._load_fitz()
        return self._page_count
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """Retorna metadados do documento."""
        if self._metadata is None:
            self._load_fitz()
            self._metadata = self._fitz_doc.metadata or {}
        return self._metadata
    
    def extract_text(self, pages: Optional[List[int]] = None, 
                     method: str = "auto") -> str:
        """
        Extrai texto do documento.
        
        Args:
            pages: Lista de páginas para extrair (None = todas)
            method: Método de extração ("fitz", "pdfplumber", "auto")
            
        Returns:
            Texto extraído do documento
        """
        extractor = TextExtractor(self)
        return extractor.extract(pages=pages, method=method)
    
    def extract_images(self, pages: Optional[List[int]] = None) -> List[Dict]:
        """
        Extrai imagens do documento.
        
        Args:
            pages: Lista de páginas para extrair (None = todas)
            
        Returns:
            Lista de dicionários com informações das imagens
        """
        extractor = ImageExtractor(self)
        return extractor.extract(pages=pages)
    
    def clean(self, options: Optional[Dict[str, Any]] = None) -> 'PDFDocument':
        """
        Limpa e processa o documento, removendo sujeiras e artefatos.
        
        Args:
            options: Opções de limpeza
            
        Returns:
            Self para chaining
        """
        cleaner = DocumentCleaner(self)
        cleaner.clean(options=options)
        return self
    
    def export(self, output_path: Union[str, Path], format: str = "text",
               **kwargs) -> None:
        """
        Exporta o documento para outro formato.
        
        Args:
            output_path: Caminho de saída
            format: Formato de exportação ("text", "markdown", "json", "html")
            **kwargs: Argumentos adicionais para o exportador
        """
        from ..formats import ExportManager
        
        output_path = Path(output_path)
        manager = ExportManager()
        manager.export(self, output_path, format=format, **kwargs)
    
    def get_page_text(self, page_num: int, method: str = "auto") -> str:
        """
        Extrai texto de uma página específica.
        
        Args:
            page_num: Número da página (0-based)
            method: Método de extração
            
        Returns:
            Texto da página
        """
        return self.extract_text(pages=[page_num], method=method)
    
    def close(self):
        """Fecha os recursos do documento."""
        if self._fitz_doc:
            self._fitz_doc.close()
            self._fitz_doc = None
        if self._pdfplumber_doc:
            self._pdfplumber_doc.close()
            self._pdfplumber_doc = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def __del__(self):
        self.close()

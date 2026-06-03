"""
Extratores de texto e imagens de documentos PDF.
"""

import fitz
import pdfplumber
from typing import Optional, List, Dict, Any, Union
from pathlib import Path


class TextExtractor:
    """
    Extrator de texto para documentos PDF.
    
    Suporta múltiplos métodos de extração para lidar com diferentes tipos de PDF.
    """
    
    def __init__(self, document):
        """
        Inicializa o extrator de texto.
        
        Args:
            document: Instância de PDFDocument
        """
        self.document = document
        
    def extract(self, pages: Optional[List[int]] = None, 
                method: str = "auto") -> str:
        """
        Extrai texto do documento.
        
        Args:
            pages: Lista de páginas para extrair (None = todas)
            method: Método de extração ("fitz", "pdfplumber", "auto", "ocr")
            
        Returns:
            Texto extraído
        """
        if method == "auto":
            method = self._detect_best_method()
        
        if method == "fitz":
            return self._extract_with_fitz(pages)
        elif method == "pdfplumber":
            return self._extract_with_pdfplumber(pages)
        elif method == "ocr":
            return self._extract_with_ocr(pages)
        else:
            raise ValueError(f"Método de extração desconhecido: {method}")
    
    def _detect_best_method(self) -> str:
        """Detecta o melhor método de extração baseado no tipo de PDF."""
        self.document._load_fitz()
        
        # Tenta extrair texto com fitz para verificar se há texto nativo
        first_page = self.document._fitz_doc[0]
        text = first_page.get_text("text").strip()
        
        if len(text) > 100:
            return "fitz"
        else:
            # PDF pode ser digitalizado/escaneado
            return "ocr"
    
    def _extract_with_fitz(self, pages: Optional[List[int]] = None) -> str:
        """Extrai texto usando PyMuPDF (fitz)."""
        self.document._load_fitz()
        
        if pages is None:
            pages = range(self.document.page_count)
        
        texts = []
        for page_num in pages:
            if 0 <= page_num < self.document.page_count:
                page = self.document._fitz_doc[page_num]
                text = page.get_text("text")
                texts.append(text)
        
        return "\n\n".join(texts)
    
    def _extract_with_pdfplumber(self, pages: Optional[List[int]] = None) -> str:
        """Extrai texto usando pdfplumber (melhor para tabelas)."""
        self.document._load_pdfplumber()
        
        if pages is None:
            pages = range(len(self.document._pdfplumber_doc.pages))
        
        texts = []
        for page_num in pages:
            if 0 <= page_num < len(self.document._pdfplumber_doc.pages):
                page = self.document._pdfplumber_doc.pages[page_num]
                text = page.extract_text() or ""
                texts.append(text)
        
        return "\n\n".join(texts)
    
    def _extract_with_ocr(self, pages: Optional[List[int]] = None) -> str:
        """Extrai texto usando OCR (para PDFs digitalizados)."""
        try:
            import pytesseract
            from PIL import Image
            import io
        except ImportError:
            raise ImportError(
                "pytesseract e Pillow são necessários para OCR. "
                "Instale com: pip install pytesseract Pillow"
            )
        
        self.document._load_fitz()
        
        if pages is None:
            pages = range(self.document.page_count)
        
        texts = []
        for page_num in pages:
            if 0 <= page_num < self.document.page_count:
                page = self.document._fitz_doc[page_num]
                # Renderiza página como imagem
                pix = page.get_pixmap(dpi=300)
                img_data = pix.tobytes("png")
                
                # Processa com OCR
                img = Image.open(io.BytesIO(img_data))
                text = pytesseract.image_to_string(img, lang='por+eng')
                texts.append(text)
        
        return "\n\n".join(texts)


class ImageExtractor:
    """
    Extrator de imagens de documentos PDF.
    """
    
    def __init__(self, document):
        """
        Inicializa o extrator de imagens.
        
        Args:
            document: Instância de PDFDocument
        """
        self.document = document
        
    def extract(self, pages: Optional[List[int]] = None) -> List[Dict[str, Any]]:
        """
        Extrai imagens do documento.
        
        Args:
            pages: Lista de páginas para extrair (None = todas)
            
        Returns:
            Lista de dicionários com informações das imagens
        """
        self.document._load_fitz()
        
        if pages is None:
            pages = range(self.document.page_count)
        
        images = []
        for page_num in pages:
            if 0 <= page_num < self.document.page_count:
                page = self.document._fitz_doc[page_num]
                image_list = page.get_images(full=True)
                
                for img_index, img_info in enumerate(image_list):
                    xref = img_info[0]
                    try:
                        base_image = self.document._fitz_doc.extract_image(xref)
                        if base_image:
                            image_data = {
                                "page": page_num,
                                "index": img_index,
                                "width": base_image["width"],
                                "height": base_image["height"],
                                "colorspace": base_image["colorspace"],
                                "data": base_image["image"],
                                "ext": base_image["ext"],
                            }
                            images.append(image_data)
                    except Exception as e:
                        # Alguns PDFs têm imagens corrompidas
                        continue
        
        return images
    
    def save_images(self, output_dir: Union[str, Path], 
                    pages: Optional[List[int]] = None) -> List[Path]:
        """
        Salva imagens extraídas em um diretório.
        
        Args:
            output_dir: Diretório de saída
            pages: Páginas para extrair
            
        Returns:
            Lista de caminhos das imagens salvas
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        images = self.extract(pages=pages)
        saved_paths = []
        
        for img_info in images:
            filename = f"page_{img_info['page']:04d}_img_{img_info['index']:04d}.{img_info['ext']}"
            output_path = output_dir / filename
            
            with open(output_path, "wb") as f:
                f.write(img_info["data"])
            
            saved_paths.append(output_path)
        
        return saved_paths

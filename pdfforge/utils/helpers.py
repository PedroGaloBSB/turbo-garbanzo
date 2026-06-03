"""
Funções utilitárias para análise e detecção de tipos de PDF.
"""

import fitz
from pathlib import Path
from typing import Union, Dict, Any


def detect_pdf_type(file_path: Union[str, Path]) -> str:
    """
    Detecta o tipo de PDF (texto, imagem, digitalizado, misto).
    
    Args:
        file_path: Caminho para o arquivo PDF
        
    Returns:
        Tipo do PDF: "text", "image", "scanned", "mixed"
    """
    file_path = Path(file_path)
    doc = fitz.open(file_path)
    
    text_pages = 0
    image_pages = 0
    total_pages = len(doc)
    
    for page_num in range(total_pages):
        page = doc[page_num]
        
        # Verifica se há texto
        text = page.get_text("text").strip()
        has_text = len(text) > 50
        
        # Verifica se há imagens
        images = page.get_images(full=True)
        has_images = len(images) > 0
        
        if has_text and not has_images:
            text_pages += 1
        elif has_images and not has_text:
            image_pages += 1
        elif has_text and has_images:
            text_pages += 1  # Considera como página de texto
    
    doc.close()
    
    if total_pages == 0:
        return "empty"
    elif text_pages == total_pages:
        return "text"
    elif image_pages == total_pages:
        return "image"
    elif text_pages > 0 and image_pages > 0:
        return "mixed"
    else:
        return "scanned"


def is_scanned_pdf(file_path: Union[str, Path]) -> bool:
    """
    Verifica se um PDF é digitalizado/escaneado (sem texto nativo).
    
    Args:
        file_path: Caminho para o arquivo PDF
        
    Returns:
        True se for digitalizado, False caso contrário
    """
    file_path = Path(file_path)
    doc = fitz.open(file_path)
    
    # Verifica as primeiras 3 páginas
    pages_to_check = min(3, len(doc))
    
    for page_num in range(pages_to_check):
        page = doc[page_num]
        text = page.get_text("text").strip()
        
        # Se encontrar texto significativo, não é scanned
        if len(text) > 100:
            doc.close()
            return False
    
    doc.close()
    return True


def get_pdf_info(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Obtém informações detalhadas sobre um PDF.
    
    Args:
        file_path: Caminho para o arquivo PDF
        
    Returns:
        Dicionário com informações do PDF
    """
    file_path = Path(file_path)
    doc = fitz.open(file_path)
    
    info = {
        "file_name": file_path.name,
        "file_size": file_path.stat().st_size,
        "page_count": len(doc),
        "metadata": doc.metadata or {},
        "type": detect_pdf_type(file_path),
        "is_encrypted": doc.is_encrypted,
        "pages": [],
    }
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        text = page.get_text("text").strip()
        images = page.get_images(full=True)
        
        page_info = {
            "number": page_num,
            "width": page.rect.width,
            "height": page.rect.height,
            "text_length": len(text),
            "image_count": len(images),
        }
        
        info["pages"].append(page_info)
    
    doc.close()
    return info


def validate_pdf(file_path: Union[str, Path]) -> bool:
    """
    Valida se um arquivo é um PDF válido.
    
    Args:
        file_path: Caminho para o arquivo
        
    Returns:
        True se for um PDF válido
    """
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            return False
        
        # Verifica magic bytes do PDF
        with open(file_path, 'rb') as f:
            header = f.read(4)
            if header != b'%PDF':
                return False
        
        # Tenta abrir com fitz
        doc = fitz.open(file_path)
        is_valid = len(doc) > 0
        doc.close()
        
        return is_valid
    except Exception:
        return False

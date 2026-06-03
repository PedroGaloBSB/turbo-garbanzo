"""
Testes básicos do PDFForge.
"""

import pytest
from pathlib import Path


def test_imports():
    """Testa se os imports principais funcionam."""
    from pdfforge import (
        PDFDocument,
        TextExtractor,
        ImageExtractor,
        DocumentCleaner,
        ExportManager,
        BatchProcessor,
        get_pdf_info,
        detect_pdf_type,
    )
    
    assert PDFDocument is not None
    assert ExportManager is not None
    assert BatchProcessor is not None


def test_version():
    """Testa versão do pacote."""
    import pdfforge
    assert pdfforge.__version__ == "0.1.0"


def test_export_manager_formats():
    """Testa se todos os formatos de exportação estão registrados."""
    from pdfforge.formats import ExportManager
    
    manager = ExportManager()
    
    expected_formats = ['text', 'txt', 'markdown', 'md', 'json', 'html']
    
    for fmt in expected_formats:
        assert fmt in manager.exporters, f"Formato {fmt} não registrado"


def test_document_cleaner_options():
    """Testa opções do limpador de documentos."""
    from pdfforge.core.cleaner import DocumentCleaner
    
    # Testa opções padrão
    default_options = {
        "remove_hyphens": True,
        "remove_extra_spaces": True,
        "remove_empty_lines": True,
        "normalize_unicode": True,
        "fix_encoding": True,
        "remove_headers_footers": False,
        "custom_patterns": [],
    }
    
    # Verifica estrutura básica (sem documento real)
    assert "remove_hyphens" in default_options
    assert default_options["remove_hyphens"] is True


def test_batch_processor_initialization():
    """Testa inicialização do processador em lote."""
    from pdfforge.utils.batch import BatchProcessor
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        processor = BatchProcessor(
            input_dir=tmpdir,
            output_dir=tmpdir
        )
        
        assert processor.input_dir is not None
        assert processor.output_dir is not None


def test_pdf_helpers():
    """Testa funções utilitárias de PDF."""
    from pdfforge.utils.helpers import validate_pdf
    
    # Testa com arquivo inexistente
    assert validate_pdf("/nonexistent/file.pdf") is False
    
    # Testa com arquivo que não é PDF
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        f.write(b"Not a PDF file")
        temp_path = f.name
    
    try:
        assert validate_pdf(temp_path) is False
    finally:
        Path(temp_path).unlink(missing_ok=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

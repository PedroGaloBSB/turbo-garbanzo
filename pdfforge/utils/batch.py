"""
Processamento em lote de múltiplos arquivos PDF.
"""

from pathlib import Path
from typing import List, Union, Optional, Callable, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import json


class BatchProcessor:
    """
    Processador em lote para múltiplos arquivos PDF.
    
    Permite processar vários PDFs de forma eficiente com suporte a paralelismo.
    """
    
    def __init__(self, input_dir: Optional[Union[str, Path]] = None,
                 output_dir: Optional[Union[str, Path]] = None):
        """
        Inicializa o processador em lote.
        
        Args:
            input_dir: Diretório de entrada (opcional)
            output_dir: Diretório de saída (opcional)
        """
        self.input_dir = Path(input_dir) if input_dir else None
        self.output_dir = Path(output_dir) if output_dir else None
        
        if self.output_dir:
            self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def find_pdfs(self, directory: Optional[Union[str, Path]] = None,
                  recursive: bool = True) -> List[Path]:
        """
        Encontra arquivos PDF em um diretório.
        
        Args:
            directory: Diretório para buscar (padrão: input_dir)
            recursive: Buscar recursivamente em subdiretórios
            
        Returns:
            Lista de caminhos de arquivos PDF
        """
        directory = Path(directory) if directory else self.input_dir
        
        if not directory:
            raise ValueError("Diretório não especificado")
        
        pattern = "**/*.pdf" if recursive else "*.pdf"
        pdfs = list(directory.glob(pattern))
        
        return sorted(pdfs)
    
    def process(self, pdf_files: Optional[List[Union[str, Path]]] = None,
                processor_func: Optional[Callable] = None,
                max_workers: int = 4,
                **kwargs) -> List[Dict[str, Any]]:
        """
        Processa múltiplos PDFs em paralelo.
        
        Args:
            pdf_files: Lista de arquivos PDF para processar
            processor_func: Função customizada para processar cada PDF
                           Deve receber (pdf_path, **kwargs) e retornar um dict
            max_workers: Número máximo de workers para processamento paralelo
            **kwargs: Argumentos adicionais para a função de processamento
            
        Returns:
            Lista de resultados do processamento
        """
        from .core.document import PDFDocument
        
        if pdf_files is None:
            pdf_files = self.find_pdfs()
        else:
            pdf_files = [Path(f) for f in pdf_files]
        
        if not pdf_files:
            return []
        
        results = []
        
        def default_processor(pdf_path: Path, **kwargs):
            """Processador padrão que extrai informações básicas."""
            try:
                with PDFDocument(pdf_path) as doc:
                    text = doc.extract_text()
                    cleaner = doc.clean()
                    
                    result = {
                        "file": str(pdf_path),
                        "file_name": pdf_path.name,
                        "success": True,
                        "page_count": doc.page_count,
                        "metadata": doc.metadata,
                        "text_length": len(text),
                        "word_count": len(text.split()),
                        "cleaned_text": cleaner,
                    }
                    
                    # Se output_dir especificado, exporta para JSON
                    if kwargs.get("output_dir"):
                        output_dir = Path(kwargs["output_dir"])
                        output_dir.mkdir(parents=True, exist_ok=True)
                        
                        output_file = output_dir / f"{pdf_path.stem}.json"
                        with open(output_file, 'w', encoding='utf-8') as f:
                            json.dump(result, f, ensure_ascii=False, indent=2)
                        
                        result["output_file"] = str(output_file)
                    
                    return result
                    
            except Exception as e:
                return {
                    "file": str(pdf_path),
                    "file_name": pdf_path.name,
                    "success": False,
                    "error": str(e),
                }
        
        processor = processor_func if processor_func else default_processor
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(processor, pdf_file, **kwargs): pdf_file
                for pdf_file in pdf_files
            }
            
            for future in as_completed(futures):
                pdf_file = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append({
                        "file": str(pdf_file),
                        "file_name": pdf_file.name,
                        "success": False,
                        "error": str(e),
                    })
        
        return results
    
    def export_all(self, pdf_files: Optional[List[Union[str, Path]]] = None,
                   format: str = "json",
                   output_dir: Optional[Union[str, Path]] = None,
                   max_workers: int = 4) -> List[Path]:
        """
        Exporta múltiplos PDFs para um formato específico.
        
        Args:
            pdf_files: Lista de arquivos PDF
            format: Formato de exportação
            output_dir: Diretório de saída
            max_workers: Número de workers
            
        Returns:
            Lista de arquivos exportados
        """
        from .core.document import PDFDocument
        
        if pdf_files is None:
            pdf_files = self.find_pdfs()
        else:
            pdf_files = [Path(f) for f in pdf_files]
        
        output_dir = Path(output_dir) if output_dir else self.output_dir
        
        if not output_dir:
            raise ValueError("Diretório de saída não especificado")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        exported_files = []
        
        def export_pdf(pdf_path: Path):
            try:
                with PDFDocument(pdf_path) as doc:
                    output_file = output_dir / f"{pdf_path.stem}.{format}"
                    doc.export(output_file, format=format)
                    return {"success": True, "file": str(output_file)}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(export_pdf, pdf_file): pdf_file
                for pdf_file in pdf_files
            }
            
            for future in as_completed(futures):
                result = future.result()
                if result["success"]:
                    exported_files.append(Path(result["file"]))
        
        return exported_files
    
    def merge_pdfs(self, pdf_files: Optional[List[Union[str, Path]]] = None,
                   output_path: Optional[Union[str, Path]] = None) -> Path:
        """
        Mescla múltiplos PDFs em um único arquivo.
        
        Args:
            pdf_files: Lista de arquivos PDF para mesclar
            output_path: Caminho do arquivo de saída
            
        Returns:
            Caminho do arquivo mesclado
        """
        import fitz
        
        if pdf_files is None:
            pdf_files = self.find_pdfs()
        else:
            pdf_files = [Path(f) for f in pdf_files]
        
        if not pdf_files:
            raise ValueError("Nenhum arquivo PDF para mesclar")
        
        output_path = Path(output_path) if output_path else (self.output_dir / "merged.pdf")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        merged_doc = fitz.open()
        
        for pdf_file in pdf_files:
            doc = fitz.open(pdf_file)
            merged_doc.insert_pdf(doc)
            doc.close()
        
        merged_doc.save(output_path)
        merged_doc.close()
        
        return output_path

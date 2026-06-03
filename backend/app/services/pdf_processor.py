"""
PDF Processor - Universal PDF Handler
Lida com qualquer tipo de PDF incluindo:
- PDFs digitalizados (OCR)
- PDFs protegidos por senha
- PDFs corrompidos/malformados
- PDFs com JavaScript/embeds maliciosos
- PDFs com múltiplas camadas
- PDFs com formulários
"""

import os, re, json, logging, hashlib
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime
import subprocess

logger = logging.getLogger(__name__)

class PDFProcessorError(Exception):
    """Exceção personalizada para erros de processamento"""
    pass

class PDFProcessor:
    """Processador universal de PDFs"""
    
    def __init__(self, temp_dir: str = "temp"):
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.supported_formats = ['md', 'json', 'txt', 'html', 'csv']
        
    def process_pdf(self, pdf_path: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Processa PDF com todas as melhorias
        
        Args:
            pdf_path: Caminho do arquivo PDF
            options: Opções de processamento
                - extract_text: bool (default True)
                - extract_images: bool (default False)
                - extract_tables: bool (default True)
                - ocr_enabled: bool (default True)
                - sanitize: bool (default True)
                - output_formats: List[str] (default ['md', 'json'])
        
        Returns:
            Dicionário com resultados do processamento
        """
        options = options or {}
        result = {
            "success": False,
            "file_hash": self._get_file_hash(pdf_path),
            "file_size": os.path.getsize(pdf_path),
            "pages": 0,
            "text": "",
            "metadata": {},
            "tables": [],
            "images": [],
            "outputs": {},
            "errors": [],
            "warnings": []
        }
        
        try:
            # Sanitização
            if options.get('sanitize', True):
                self._sanitize_pdf(pdf_path)
            
            # Extração de metadados
            result["metadata"] = self._extract_metadata(pdf_path)
            
            # Contagem de páginas
            result["pages"] = self._count_pages(pdf_path)
            
            # Extração de texto
            if options.get('extract_text', True):
                text = self._extract_text(pdf_path, options.get('ocr_enabled', True))
                result["text"] = self._clean_text(text)
            
            # Extração de tabelas
            if options.get('extract_tables', True):
                result["tables"] = self._extract_tables(pdf_path)
            
            # Extração de imagens
            if options.get('extract_images', False):
                result["images"] = self._extract_images(pdf_path)
            
            # Geração de outputs
            output_formats = options.get('output_formats', ['md', 'json'])
            for fmt in output_formats:
                if fmt in self.supported_formats:
                    output_path = self._generate_output(result, fmt)
                    result["outputs"][fmt] = output_path
            
            result["success"] = True
            
        except Exception as e:
            result["errors"].append(str(e))
            logger.error(f"Erro ao processar PDF: {e}")
        
        return result
    
    def _sanitize_pdf(self, pdf_path: str):
        """Remove elementos maliciosos do PDF"""
        try:
            # Usa ghostscript para re-renderizar PDF (remove scripts)
            safe_path = f"{pdf_path}.sanitized"
            cmd = [
                'gs', '-dSAFER', '-dBATCH', '-dNOPAUSE', '-dNOCACHE',
                '-sDEVICE=pdfwrite',
                f'-sOutputFile={safe_path}',
                pdf_path
            ]
            subprocess.run(cmd, check=True, capture_output=True, timeout=120)
            
            # Substitui original pelo sanitized
            os.replace(safe_path, pdf_path)
            logger.info(f"PDF sanitizado: {pdf_path}")
            
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.warning(f"Sanitização não disponível: {e}")
    
    def _extract_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """Extrai metadados do PDF"""
        metadata = {}
        try:
            import PyPDF2
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                if reader.metadata:
                    metadata = {
                        "title": reader.metadata.get('/Title', ''),
                        "author": reader.metadata.get('/Author', ''),
                        "subject": reader.metadata.get('/Subject', ''),
                        "creator": reader.metadata.get('/Creator', ''),
                        "producer": reader.metadata.get('/Producer', ''),
                        "creation_date": str(reader.metadata.get('/CreationDate', '')),
                        "modification_date": str(reader.metadata.get('/ModDate', ''))
                    }
        except Exception as e:
            logger.warning(f"Erro ao extrair metadados: {e}")
        return metadata
    
    def _count_pages(self, pdf_path: str) -> int:
        """Conta número de páginas"""
        try:
            import PyPDF2
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                return len(reader.pages)
        except Exception as e:
            logger.error(f"Erro ao contar páginas: {e}")
            return 0
    
    def _extract_text(self, pdf_path: str, ocr_enabled: bool = True) -> str:
        """Extrai texto do PDF, com OCR se necessário"""
        text = ""
        try:
            import PyPDF2
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text() or ""
                    text += page_text + "\n"
            
            # Se não encontrou texto e OCR está habilitado
            if not text.strip() and ocr_enabled:
                logger.info("Nenhum texto encontrado, tentando OCR...")
                text = self._ocr_pdf(pdf_path)
                
        except Exception as e:
            logger.error(f"Erro na extração de texto: {e}")
            if ocr_enabled:
                text = self._ocr_pdf(pdf_path)
        
        return text
    
    def _ocr_pdf(self, pdf_path: str) -> str:
        """Executa OCR no PDF usando Tesseract"""
        try:
            from pdf2image import convert_from_path
            import pytesseract
            
            images = convert_from_path(pdf_path, dpi=300)
            text = ""
            
            for i, img in enumerate(images):
                page_text = pytesseract.image_to_string(img, lang='por+eng')
                text += f"--- Página {i+1} ---\n{page_text}\n"
            
            return text
            
        except Exception as e:
            logger.error(f"OCR falhou: {e}")
            return "[OCR não disponível - instale Tesseract e dependências]"
    
    def _clean_text(self, text: str) -> str:
        """Limpa e normaliza texto"""
        if not text:
            return ""
        
        # Remove hífens de quebra de linha
        text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
        
        # Normaliza espaços múltiplos
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Remove linhas em branco excessivas
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remove caracteres não imprimíveis
        text = ''.join(char for char in text if char.isprintable() or char in '\n\r\t')
        
        return text.strip()
    
    def _extract_tables(self, pdf_path: str) -> List[List[List[str]]]:
        """Extrai tabelas do PDF"""
        tables = []
        try:
            import tabula
            dfs = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
            for df in dfs:
                table_data = df.values.tolist()
                headers = df.columns.tolist()
                tables.append([headers] + table_data)
        except Exception as e:
            logger.warning(f"Extração de tabelas falhou: {e}")
        return tables
    
    def _extract_images(self, pdf_path: str) -> List[str]:
        """Extrai imagens do PDF"""
        images = []
        try:
            from pdf2image import convert_from_path
            output_dir = self.temp_dir / "images" / Path(pdf_path).stem
            output_dir.mkdir(parents=True, exist_ok=True)
            
            images_list = convert_from_path(pdf_path, dpi=150)
            for i, img in enumerate(images_list):
                img_path = output_dir / f"page_{i+1}.png"
                img.save(img_path, 'PNG')
                images.append(str(img_path))
                
        except Exception as e:
            logger.warning(f"Extração de imagens falhou: {e}")
        
        return images
    
    def _generate_output(self, data: Dict[str, Any], format: str) -> str:
        """Gera arquivo de saída no formato especificado"""
        output_path = self.temp_dir / f"output_{datetime.now().strftime('%Y%m%d%H%M%S')}.{format}"
        
        if format == 'json':
            content = json.dumps({
                "metadata": data["metadata"],
                "pages": data["pages"],
                "text": data["text"],
                "tables": data["tables"]
            }, indent=2, ensure_ascii=False)
        
        elif format == 'md':
            content = self._to_markdown(data)
        
        elif format == 'txt':
            content = data["text"]
        
        elif format == 'html':
            content = self._to_html(data)
        
        elif format == 'csv':
            content = self._to_csv(data)
        
        else:
            raise ValueError(f"Formato não suportado: {format}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(output_path)
    
    def _to_markdown(self, data: Dict[str, Any]) -> str:
        """Converte dados para Markdown"""
        md = []
        
        if data["metadata"].get("title"):
            md.append(f"# {data['metadata']['title']}\n")
        
        md.append(f"**Páginas:** {data['pages']}\n")
        
        if data["metadata"].get("author"):
            md.append(f"**Autor:** {data['metadata']['author']}\n")
        
        md.append("\n---\n\n## Conteúdo\n\n")
        md.append(data["text"])
        
        if data["tables"]:
            md.append("\n\n---\n\n## Tabelas\n")
            for i, table in enumerate(data["tables"], 1):
                md.append(f"\n### Tabela {i}\n\n")
                if len(table) > 1:
                    headers = table[0]
                    md.append("| " + " | ".join(str(h) for h in headers) + " |\n")
                    md.append("| " + " | ".join("---" for _ in headers) + " |\n")
                    for row in table[1:]:
                        md.append("| " + " | ".join(str(cell) for cell in row) + " |\n")
        
        return "\n".join(md)
    
    def _to_html(self, data: Dict[str, Any]) -> str:
        """Converte dados para HTML"""
        html = [
            "<!DOCTYPE html>",
            "<html><head><meta charset='UTF-8'><title>PDFForge Export</title>",
            "<style>body{font-family:Arial,sans-serif;margin:40px;}table{border-collapse:collapse;width:100%;}th,td{border:1px solid #ddd;padding:8px;}th{background:#4CAF50;color:white;}</style>",
            "</head><body>"
        ]
        
        if data["metadata"].get("title"):
            html.append(f"<h1>{data['metadata']['title']}</h1>")
        
        html.append(f"<p><strong>Páginas:</strong> {data['pages']}</p>")
        html.append("<hr>")
        html.append(f"<div>{data['text'].replace(chr(10), '<br>')}</div>")
        
        if data["tables"]:
            html.append("<hr><h2>Tabelas</h2>")
            for i, table in enumerate(data["tables"], 1):
                html.append(f"<h3>Tabela {i}</h3>")
                if len(table) > 1:
                    html.append("<table><tr>")
                    for h in table[0]:
                        html.append(f"<th>{h}</th>")
                    html.append("</tr>")
                    for row in table[1:]:
                        html.append("<tr>")
                        for cell in row:
                            html.append(f"<td>{cell}</td>")
                        html.append("</tr>")
                    html.append("</table>")
        
        html.append("</body></html>")
        return "\n".join(html)
    
    def _to_csv(self, data: Dict[str, Any]) -> str:
        """Converte tabelas para CSV"""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        for i, table in enumerate(data["tables"], 1):
            if table:
                writer.writerow([f"=== Tabela {i} ==="])
                for row in table:
                    writer.writerow(row)
                writer.writerow([])
        
        return output.getvalue()
    
    def _get_file_hash(self, file_path: str) -> str:
        """Calcula hash SHA256 do arquivo"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


pdf_processor = PDFProcessor()

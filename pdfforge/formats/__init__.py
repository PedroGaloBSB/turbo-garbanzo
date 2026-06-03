"""
Módulo de exportação para diferentes formatos.

Suporta exportação para Markdown, JSON, HTML, TXT e outros formatos.
"""

import json
from pathlib import Path
from typing import Union, Dict, Any, Optional
from abc import ABC, abstractmethod


class BaseExporter(ABC):
    """Classe base para exportadores."""
    
    @abstractmethod
    def export(self, document, output_path: Path, **kwargs) -> None:
        """Exporta o documento para um arquivo."""
        pass


class TextExporter(BaseExporter):
    """Exportador para texto simples."""
    
    def export(self, document, output_path: Path, **kwargs) -> None:
        text = document.extract_text()
        
        # Se houve limpeza, usa o texto limpo
        if hasattr(document, '_cleaned_text') and document._cleaned_text:
            text = document._cleaned_text
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)


class MarkdownExporter(BaseExporter):
    """Exportador para Markdown."""
    
    def export(self, document, output_path: Path, 
               include_metadata: bool = True,
               extract_tables: bool = True,
               **kwargs) -> None:
        """
        Exporta para Markdown.
        
        Args:
            document: PDFDocument
            output_path: Caminho de saída
            include_metadata: Incluir metadados no início
            extract_tables: Tentar extrair e formatar tabelas
        """
        lines = []
        
        # Metadados
        if include_metadata:
            lines.append("# Documento PDF\n")
            lines.append("## Metadados\n")
            metadata = document.metadata
            for key, value in metadata.items():
                if value:
                    lines.append(f"- **{key}**: {value}")
            lines.append("")
            lines.append(f"- **Páginas**: {document.page_count}")
            lines.append("")
        
        # Conteúdo principal
        lines.append("## Conteúdo\n")
        
        text = document.extract_text(method="fitz")
        
        # Divide por páginas (aproximado)
        pages_text = text.split('\n\n')
        
        current_page = 0
        for i, block in enumerate(pages_text):
            if block.strip():
                # Tenta detectar início de nova página
                if len(block) > 1000 or i % 10 == 0:
                    current_page += 1
                
                lines.append(block)
                lines.append("")
        
        # Tabelas
        if extract_tables:
            from ..core.cleaner import DocumentCleaner
            cleaner = DocumentCleaner(document)
            tables = cleaner.extract_tables()
            if tables:
                lines.append("\n## Tabelas\n")
                for table_idx, table in enumerate(tables, 1):
                    lines.append(f"### Tabela {table_idx}\n")
                    if table:
                        # Header
                        header = table[0]
                        lines.append("| " + " | ".join(str(c) or "" for c in header) + " |")
                        lines.append("| " + " | ".join("---" for _ in header) + " |")
                        
                        # Rows
                        for row in table[1:]:
                            lines.append("| " + " | ".join(str(c) or "" for c in row) + " |")
                        lines.append("")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))


class JSONExporter(BaseExporter):
    """Exportador para JSON."""
    
    def export(self, document, output_path: Path,
               pretty: bool = True,
               include_text: bool = True,
               include_tables: bool = True,
               include_images_info: bool = False,
               **kwargs) -> None:
        """
        Exporta para JSON.
        
        Args:
            document: PDFDocument
            output_path: Caminho de saída
            pretty: Formatar com indentação
            include_text: Incluir texto completo
            include_tables: Incluir tabelas extraídas
            include_images_info: Incluir informações das imagens
        """
        data = {}
        
        # Metadados
        data["metadata"] = document.metadata
        data["page_count"] = document.page_count
        data["file_name"] = document.file_path.name
        
        # Texto limpo
        if include_text:
            text = document.extract_text(method="fitz")
            data["text"] = text
            data["word_count"] = len(data["text"].split())
            data["char_count"] = len(data["text"])
        
        # Tabelas
        if include_tables:
            from ..core.cleaner import DocumentCleaner
            cleaner = DocumentCleaner(document)
            data["tables"] = cleaner.extract_tables()
        
        # Informações de imagens
        if include_images_info:
            images = document.extract_images()
            data["images"] = [
                {
                    "page": img["page"],
                    "width": img["width"],
                    "height": img["height"],
                    "ext": img["ext"],
                }
                for img in images
            ]
        
        # Dados estruturados (emails, phones, urls)
        structured = cleaner.extract_structured_data()
        data["emails"] = structured.get("emails", [])
        data["phones"] = structured.get("phones", [])
        data["urls"] = structured.get("urls", [])
        
        # Escreve JSON
        indent = 2 if pretty else None
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)


class HTMLExporter(BaseExporter):
    """Exportador para HTML."""
    
    def export(self, document, output_path: Path,
               include_css: bool = True,
               **kwargs) -> None:
        """
        Exporta para HTML.
        
        Args:
            document: PDFDocument
            output_path: Caminho de saída
            include_css: Incluir CSS básico para estilização
        """
        text = document.extract_text(method="fitz")
        
        # Converte quebras de linha em parágrafos
        paragraphs = text.split('\n\n')
        html_content = ""
        
        for para in paragraphs:
            if para.strip():
                html_content += f"<p>{para.strip()}</p>\n"
        
        # Tabelas
        if include_tables:
            from ..core.cleaner import DocumentCleaner
            cleaner = DocumentCleaner(document)
            tables = cleaner.extract_tables()
            if tables:
                for table in tables:
                    if table:
                        html_content += "<table>\n"
                        # Header
                        html_content += "<thead><tr>"
                        for cell in table[0]:
                            html_content += f"<th>{cell or ''}</th>"
                        html_content += "</tr></thead>\n"
                        
                        # Body
                        html_content += "<tbody>\n"
                        for row in table[1:]:
                            html_content += "<tr>"
                            for cell in row:
                                html_content += f"<td>{cell or ''}</td>"
                            html_content += "</tr>\n"
                        html_content += "</tbody>\n"
                        html_content += "</table>\n"
        
        css = """
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; line-height: 1.6; }
            p { margin-bottom: 1em; }
            table { border-collapse: collapse; width: 100%; margin: 20px 0; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            tr:nth-child(even) { background-color: #f9f9f9; }
        </style>
        """
        
        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{document.file_path.stem}</title>
    {css if include_css else ''}
</head>
<body>
{html_content}
</body>
</html>"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)


class ExportManager:
    """Gerenciador de exportação."""
    
    def __init__(self):
        self.exporters = {
            "text": TextExporter(),
            "txt": TextExporter(),
            "markdown": MarkdownExporter(),
            "md": MarkdownExporter(),
            "json": JSONExporter(),
            "html": HTMLExporter(),
        }
    
    def register_exporter(self, format_name: str, exporter: BaseExporter):
        """Registra um novo exportador."""
        self.exporters[format_name.lower()] = exporter
    
    def export(self, document, output_path: Union[str, Path], 
               format: str = "text", **kwargs) -> None:
        """
        Exporta o documento para o formato especificado.
        
        Args:
            document: PDFDocument a ser exportado
            output_path: Caminho do arquivo de saída
            format: Formato de exportação
            **kwargs: Argumentos adicionais para o exportador
        """
        output_path = Path(output_path)
        format = format.lower()
        
        # Se não tem extensão, adiciona baseado no formato
        if not output_path.suffix:
            ext_map = {
                "text": ".txt",
                "txt": ".txt",
                "markdown": ".md",
                "md": ".md",
                "json": ".json",
                "html": ".html",
            }
            output_path = output_path.with_suffix(ext_map.get(format, ".txt"))
        
        if format not in self.exporters:
            available = ", ".join(self.exporters.keys())
            raise ValueError(
                f"Formato '{format}' não suportado. "
                f"Formatos disponíveis: {available}"
            )
        
        exporter = self.exporters[format]
        exporter.export(document, output_path, **kwargs)

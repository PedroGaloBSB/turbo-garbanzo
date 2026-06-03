"""
Módulo de limpeza e processamento de documentos PDF.

Remove sujeiras, artefatos, normaliza texto e melhora a qualidade dos dados extraídos.
"""

import re
from typing import Optional, Dict, Any, List


class DocumentCleaner:
    """
    Limpador de documentos PDF.
    
    Remove sujeiras comuns, normaliza texto e melhora a qualidade dos dados.
    """
    
    def __init__(self, document):
        """
        Inicializa o limpador.
        
        Args:
            document: Instância de PDFDocument
        """
        self.document = document
        self._cleaned_text = None
        
    def clean(self, options: Optional[Dict[str, Any]] = None) -> str:
        """
        Limpa o texto do documento.
        
        Args:
            options: Opções de limpeza
                - remove_hyphens: Remove hífens de quebra de linha (padrão: True)
                - remove_extra_spaces: Remove espaços extras (padrão: True)
                - remove_empty_lines: Remove linhas vazias (padrão: True)
                - normalize_unicode: Normaliza caracteres Unicode (padrão: True)
                - fix_encoding: Corrige problemas de encoding (padrão: True)
                - remove_headers_footers: Tenta remover cabeçalhos/rodapés (padrão: False)
                - custom_patterns: Lista de padrões regex para remover
                
        Returns:
            Texto limpo
        """
        default_options = {
            "remove_hyphens": True,
            "remove_extra_spaces": True,
            "remove_empty_lines": True,
            "normalize_unicode": True,
            "fix_encoding": True,
            "remove_headers_footers": False,
            "custom_patterns": [],
        }
        
        if options:
            default_options.update(options)
        
        # Extrai texto original
        text = self.document.extract_text()
        
        # Aplica limpezas
        if default_options["fix_encoding"]:
            text = self._fix_encoding(text)
        
        if default_options["normalize_unicode"]:
            text = self._normalize_unicode(text)
        
        if default_options["remove_hyphens"]:
            text = self._remove_hyphens(text)
        
        if default_options["remove_extra_spaces"]:
            text = self._remove_extra_spaces(text)
        
        if default_options["remove_empty_lines"]:
            text = self._remove_empty_lines(text)
        
        if default_options["remove_headers_footers"]:
            text = self._remove_headers_footers(text)
        
        # Aplica padrões customizados
        for pattern in default_options.get("custom_patterns", []):
            text = re.sub(pattern, "", text)
        
        self._cleaned_text = text
        return text
    
    def _fix_encoding(self, text: str) -> str:
        """
        Corrige problemas comuns de encoding.
        
        Substitui caracteres mal codificados por suas versões corretas.
        """
        # Mapeamento de problemas comuns de encoding
        replacements = {
            'Ã§': 'ç',
            'Ã£': 'ã',
            'Ãµ': 'õ',
            'Ã¡': 'á',
            'Ã©': 'é',
            'Ã­': 'í',
            'Ã³': 'ó',
            'Ãº': 'ú',
            'Ã€': 'À',
            'Ã‚': 'Â',
            'ÃŠ': 'Ê',
            'Ã´': 'ô',
            'â€"': '–',  # en dash
            'â€""': '—',  # em dash
            'â€™': "'",   # apóstrofo
            'â€œ': '"',   # aspas duplas abertas
            'â€': '"',   # aspas duplas fechadas
            'â€¢': '•',   # bullet
            'Â': '',      # caractere stray
        }
        
        for wrong, correct in replacements.items():
            text = text.replace(wrong, correct)
        
        return text
    
    def _normalize_unicode(self, text: str) -> str:
        """Normaliza caracteres Unicode."""
        import unicodedata
        # Normaliza para NFKC (compatibilidade)
        text = unicodedata.normalize('NFKC', text)
        return text
    
    def _remove_hyphens(self, text: str) -> str:
        """
        Remove hífens de quebra de linha.
        
        Exemplo: "palavra-\nquebrada" -> "palavraquebrada"
        """
        # Remove hífen seguido de nova linha
        text = re.sub(r'-\s*\n\s*', '', text)
        return text
    
    def _remove_extra_spaces(self, text: str) -> str:
        """Remove espaços extras."""
        # Multiple spaces to single space
        text = re.sub(r'[ \t]+', ' ', text)
        # Remove leading/trailing spaces from lines
        lines = text.split('\n')
        lines = [line.strip() for line in lines]
        text = '\n'.join(lines)
        return text
    
    def _remove_empty_lines(self, text: str) -> str:
        """Remove linhas vazias consecutivas."""
        # Replace multiple newlines with double newline
        text = re.sub(r'\n\s*\n', '\n\n', text)
        # Remove leading/trailing newlines
        text = text.strip('\n')
        return text
    
    def _remove_headers_footers(self, text: str) -> str:
        """
        Tenta remover cabeçalhos e rodapés repetitivos.
        
        Esta é uma implementação básica. Pode precisar de ajustes
        específicos para cada documento.
        """
        lines = text.split('\n')
        
        # Contagem de linhas curtas (possíveis headers/footers)
        short_lines = {}
        for i, line in enumerate(lines):
            if len(line.strip()) < 50 and line.strip():
                short_lines[line.strip()] = short_lines.get(line.strip(), 0) + 1
        
        # Linhas que aparecem muitas vezes são provavelmente headers/footers
        repeated_short = [k for k, v in short_lines.items() if v > 3]
        
        # Remove essas linhas
        filtered_lines = [
            line for line in lines 
            if line.strip() not in repeated_short
        ]
        
        return '\n'.join(filtered_lines)
    
    def get_cleaned_text(self) -> Optional[str]:
        """Retorna o texto limpo."""
        return self._cleaned_text
    
    def extract_tables(self) -> List[List[List[str]]]:
        """
        Extrai tabelas do documento.
        
        Returns:
            Lista de tabelas, onde cada tabela é uma lista de linhas,
            e cada linha é uma lista de células.
        """
        try:
            self.document._load_pdfplumber()
            tables = []
            
            for page in self.document._pdfplumber_doc.pages:
                page_tables = page.extract_tables()
                if page_tables:
                    tables.extend(page_tables)
            
            return tables
        except Exception as e:
            print(f"Erro ao extrair tabelas: {e}")
            return []
    
    def extract_structured_data(self) -> Dict[str, Any]:
        """
        Extrai dados estruturados do documento.
        
        Returns:
            Dicionário com dados estruturados
        """
        text = self.clean()
        
        # Extrai informações básicas
        data = {
            "metadata": self.document.metadata,
            "page_count": self.document.page_count,
            "text": text,
            "tables": self.extract_tables(),
            "word_count": len(text.split()),
            "char_count": len(text),
        }
        
        # Tenta extrair padrões comuns
        emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        phones = re.findall(r'\+?\d[\d\s\-\(\)]{8,}\d', text)
        urls = re.findall(r'https?://\S+', text)
        
        data["emails"] = list(set(emails))
        data["phones"] = list(set(phones))
        data["urls"] = list(set(urls))
        
        return data

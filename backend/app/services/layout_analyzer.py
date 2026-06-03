"""
Serviço de Análise de Layout Inteligente
Focado em documentos complexos: DOUs, Jornais, Provas de Concursos (Múltiplas Colunas)
"""
import fitz  # PyMuPDF
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import re

@dataclass
class TextBlock:
    x0: float
    y0: float
    x1: float
    y1: float
    text: str
    font_size: float
    column_id: int = -1  # Será preenchido na análise

class LayoutAnalyzer:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        
    def analyze_page_layout(self, page_num: int) -> List[TextBlock]:
        """
        Extrai blocos de texto com coordenadas precisas para análise de layout.
        """
        page = self.doc[page_num]
        blocks = []
        
        # Extrai texto com detalhes (flags=0 para texto básico, ou flags mais altos para detalhes)
        # Usamos 'dict' para obter coordenadas exatas de cada bloco
        text_dict = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
        
        for block in text_dict.get("blocks", []):
            if block.get("type") == 0:  # Apenas blocos de texto (ignora imagens)
                for line in block.get("lines", []):
                    # Junta spans da mesma linha
                    line_text = "".join([span["text"] for span in line["spans"]])
                    if not line_text.strip():
                        continue
                    
                    bbox = line["bbox"]
                    # Estimativa de tamanho de fonte média da linha
                    font_size = sum([s["size"] for s in line["spans"]]) / len(line["spans"])
                    
                    blocks.append(TextBlock(
                        x0=bbox[0], y0=bbox[1], x1=bbox[2], y1=bbox[3],
                        text=line_text.strip(),
                        font_size=font_size
                    ))
        return blocks

    def detect_columns(self, blocks: List[TextBlock], page_width: float) -> List[TextBlock]:
        """
        Algoritmo heurístico para detectar colunas baseando-se na distribuição horizontal (eixo X).
        Se houver um grande espaço vazio vertical no meio da página, assume-se múltiplas colunas.
        """
        if not blocks:
            return blocks

        # 1. Ordenar blocos por posição Y (topo para baixo) para analisar linhas
        # Mas para detectar colunas, precisamos olhar a distribuição de X
        
        # Heurística simples de clustering de X
        # Vamos agrupar blocos que estão alinhados verticalmente
        x_centers = [(b.x0 + b.x1) / 2 for b in blocks]
        
        # Se a maioria dos blocos cobre a largura total, é uma coluna única
        avg_width = sum([b.x1 - b.x0 for b in blocks]) / len(blocks)
        if avg_width > page_width * 0.8:
            for b in blocks: b.column_id = 0
            return blocks

        # Detecção de múltiplas colunas baseada em gaps horizontais
        # Simplificação: Dividir a página ao meio se houver poucos blocos no centro
        mid_point = page_width / 2
        margin = page_width * 0.1
        
        left_blocks = [b for b in blocks if b.x1 < mid_point - margin]
        right_blocks = [b for b in blocks if b.x0 > mid_point + margin]
        center_blocks = [b for b in blocks if mid_point - margin <= b.x0 <= mid_point + margin]

        # Se tivermos blocos significativos na esquerda e direita, e poucos no meio, são 2 colunas
        if len(left_blocks) > 5 and len(right_blocks) > 5 and len(center_blocks) < len(blocks) * 0.2:
            for b in left_blocks: b.column_id = 0
            for b in right_blocks: b.column_id = 1
            # Blocos do meio tentam associar ao mais próximo
            for b in center_blocks:
                dist_left = abs((b.x0 + b.x1)/2 - (sum([lb.x0 for lb in left_blocks])/len(left_blocks)))
                dist_right = abs((b.x0 + b.x1)/2 - (sum([rb.x0 for rb in right_blocks])/len(right_blocks)))
                b.column_id = 0 if dist_left < dist_right else 1
            return sorted(blocks, key=lambda k: (k.column_id, k.y0))
        
        # Default: ordem visual simples (topo-bottom, left-right)
        for b in blocks: b.column_id = 0
        return sorted(blocks, key=lambda k: (k.y0, k.x0))

    def identify_document_type(self, text_sample: str) -> str:
        """
        Classifica o tipo de documento baseado em palavras-chave.
        """
        text_upper = text_sample.upper()
        
        patterns = {
            "DIARIO_OFICIAL": ["DIÁRIO OFICIAL", "DOU", "JORNAL OFICIAL", "RETIFICAÇÃO", "ATO"],
            "PROVA_CONCURSO": ["QUESTÃO", "GABARITO", "ALTERNATIVA", "MARQUE A ÚNICA CORRETA"],
            "CONTRATO": ["CLÁUSULA", "CONTRATANTE", "VIGÊNCIA", "ASSINATURA"],
            "NOTA_FISCAL": ["DANFE", "CNPJ", "VALOR TOTAL", "INSCRIÇÃO ESTADUAL"]
        }
        
        max_score = 0
        doc_type = "GENERIC"
        
        for dtype, keywords in patterns.items():
            score = sum(1 for kw in keywords if kw in text_upper)
            if score > max_score:
                max_score = score
                doc_type = dtype
                
        return doc_type

    def extract_structured_text(self) -> Dict[str, Any]:
        """
        Extrai texto respeitando a estrutura de colunas e identifica o tipo de documento.
        Retorna um dicionário estruturado.
        """
        full_text_by_col = {}
        all_text_sample = ""
        doc_types = []

        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            page_width = page.rect.width
            
            blocks = self.analyze_page_layout(page_num)
            
            # Coleta amostra para classificação
            page_text = " ".join([b.text for b in blocks[:10]])
            all_text_sample += page_text
            
            # Detecta colunas e reordena
            ordered_blocks = self.detect_columns(blocks, page_width)
            
            # Agrupa texto por coluna para reconstrução fiel
            for block in ordered_blocks:
                col_id = block.column_id
                if col_id not in full_text_by_col:
                    full_text_by_col[col_id] = []
                full_text_by_col[col_id].append(block.text)

        # Reconstrói o texto final: Coluna 1 inteira, depois Coluna 2 inteira (comum em DOUs)
        # Ou intercalado por página? Em DOUs, geralmente lê-se a coluna 1 da pág 1, depois coluna 2 da pág 1.
        final_text = ""
        num_cols = len(full_text_by_col)
        
        if num_cols > 1:
            # Estratégia para múltiplas colunas: Lê coluna 1 de todas as páginas? 
            # Não, o padrão é Coluna 1 Pág 1 -> Coluna 2 Pág 1 -> Coluna 1 Pág 2...
            # Vamos simplificar: Junta tudo por coluna dentro da página e depois une páginas
            reconstructed_pages = []
            for page_num in range(len(self.doc)):
                # Re-analisar por página para não misturar páginas diferentes na lógica de coluna
                # (A implementação acima acumulou tudo, vamos ajustar a lógica de saída)
                pass 
            
            # Fallback para lógica simples de ordenação correta feita no loop anterior
            # O 'ordered_blocks' já está na ordem de leitura correta (Col 1 topo->fim, Col 2 topo->fim)
            # Precisamos apenas juntar o texto na ordem que veio do sorted final
            # Vamos refazer a extração para garantir a ordem página a página
            
            final_blocks_global = []
            for page_num in range(len(self.doc)):
                page = self.doc[page_num]
                blocks = self.analyze_page_layout(page_num)
                ordered = self.detect_columns(blocks, page.rect.width)
                final_blocks_global.extend(ordered)
            
            final_text = "\n".join([b.text for b in final_blocks_global])
        else:
            final_text = "\n".join([b.text for b in ordered_blocks]) if 'ordered_blocks' in locals() else ""

        doc_type = self.identify_document_type(all_text_sample)
        
        return {
            "text": final_text,
            "document_type": doc_type,
            "total_pages": len(self.doc),
            "detected_columns": num_cols if num_cols > 1 else 1,
            "metadata": {
                "filename": self.pdf_path,
                "analysis_status": "success"
            }
        }

    def close(self):
        self.doc.close()

def process_pdf_smart(pdf_path: str) -> Dict[str, Any]:
    """
    Função principal para processamento inteligente.
    """
    analyzer = LayoutAnalyzer(pdf_path)
    try:
        result = analyzer.extract_structured_text()
        return result
    finally:
        analyzer.close()

if __name__ == "__main__":
    # Teste unitário simples (requer um PDF de exemplo)
    print("Módulo de Análise de Layout pronto.")
    print("Suporta: DOUs, Provas, Jornais e Textos Nativos.")

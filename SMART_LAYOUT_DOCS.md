# 🧠 Análise Inteligente de Layout no PDFForge

## Visão Geral

Implementamos um **pré-processamento inteligente** que analisa a estrutura do documento ANTES da extração final, permitindo:

1. **Detecção automática de tipo de documento** (DOU, Provas, Contratos, etc.)
2. **Identificação de layout multi-coluna** (comum em jornais e diários oficiais)
3. **Reordenação correta do texto** para leitura humana
4. **Otimização do processo de extração** baseado no tipo detectado

## Como Funciona

### Fluxo com Smart Layout Ativado

```
Upload do PDF
    ↓
Sanitização (remove scripts maliciosos)
    ↓
[NOVO] Análise de Layout Inteligente
    ├── Detecta número de colunas
    ├── Classifica tipo de documento
    └── Extrai blocos de texto com coordenadas
    ↓
Reordenação do texto (coluna 1 → coluna 2 → ...)
    ↓
Extração de tabelas e imagens
    ↓
Geração de outputs (.md, .json, .txt, .html, .csv)
    ↓
Download / Google Drive
```

### Algoritmo de Detecção de Colunas

O sistema usa heurística baseada em coordenadas X dos blocos de texto:

1. **Extrai todos os blocos** com suas posições (x0, y0, x1, y1)
2. **Calcula largura média** dos blocos
3. **Se largura média > 80% da página**: Assume coluna única
4. **Se não**, divide a página ao meio e verifica:
   - Blocos à esquerda do centro
   - Blocos à direita do centro
   - Blocos no centro (gap)
5. **Se houver blocos significativos em ambos os lados** e poucos no centro:
   - Marca como 2 colunas
   - Reordena: Lê toda coluna 1, depois toda coluna 2

### Classificação de Documentos

Usa pattern matching com palavras-chave:

| Tipo | Palavras-chave Detectadas |
|------|---------------------------|
| `DIARIO_OFICIAL` | "DIÁRIO OFICIAL", "DOU", "JORNAL OFICIAL", "RETIFICAÇÃO" |
| `PROVA_CONCURSO` | "QUESTÃO", "GABARITO", "ALTERNATIVA", "MARQUE A ÚNICA CORRETA" |
| `CONTRATO` | "CLÁUSULA", "CONTRATANTE", "VIGÊNCIA", "ASSINATURA" |
| `NOTA_FISCAL` | "DANFE", "CNPJ", "VALOR TOTAL", "INSCRIÇÃO ESTADUAL" |
| `GENERIC` | Nenhum padrão acima detectado |

## Uso na API

### Endpoint de Upload

```http
POST /api/upload
Content-Type: multipart/form-data

file: [arquivo.pdf]
options: {
  "smart_layout": true,      // Ativa análise inteligente (default: true)
  "ocr_enabled": true,       // OCR para digitalizados
  "output_formats": ["md", "json"],
  "sanitize": true
}
```

### Resposta da API

```json
{
  "success": true,
  "document_type": "DIARIO_OFICIAL",
  "layout_info": {
    "columns": 2,
    "analysis_status": "success"
  },
  "text": "Texto extraído na ordem correta de leitura...",
  "outputs": {
    "md": "/downloads/file.md",
    "json": "/downloads/file.json"
  }
}
```

## Casos de Uso Específicos

### 1. Diário Oficial da União (DOU)

**Problema**: DOUs têm 2-3 colunas por página. Leitura sequencial tradicional mistura colunas.

**Solução**: 
- Detecta 2-3 colunas
- Reordena: Coluna 1 (pág 1) → Coluna 2 (pág 1) → Coluna 1 (pág 2)...
- Preserva estrutura de atos e retificações

### 2. Provas de Concurso

**Problema**: Questões em colunas, gabarito no final, múltiplas alternativas.

**Solução**:
- Identifica como `PROVA_CONCURSO`
- Separa questões por numeração
- Extrai gabarito como metadado

### 3. Jornais e Revistas

**Problema**: Layout complexo com títulos, subtítulos, colunas irregulares.

**Solução**:
- Detecta colunas dinamicamente por página
- Usa tamanho de fonte para identificar títulos
- Mantém hierarquia visual no Markdown

## Vantagens

✅ **Precisão**: Texto extraído na ordem correta de leitura humana  
✅ **Inteligência**: Sistema "entende" o tipo de documento  
✅ **Flexibilidade**: Fallback para método tradicional se falhar  
✅ **Performance**: Análise rápida antes do processamento pesado  
✅ **LGPD**: Identifica documentos sensíveis automaticamente  

## Limitações e Melhorias Futuras

⚠️ **Layouts muito complexos** (3+ colunas irregulares) podem precisar de ajuste fino  
⚠️ **Imagens com texto** ainda dependem de OCR separado  
🔮 **Futuro**: Usar ML para classificação mais precisa de layouts  

## Arquivos Implementados

- `backend/app/services/layout_analyzer.py` - Motor de análise de layout
- `backend/app/services/pdf_processor.py` - Integrado com opção `smart_layout`
- `backend/app/api/routes.py` - Endpoints atualizados

## Teste Rápido

```python
from app.services.layout_analyzer import process_pdf_smart

resultado = process_pdf_smart("exemplo_dou.pdf")
print(f"Tipo: {resultado['document_type']}")
print(f"Colunas: {resultado['detected_columns']}")
print(f"Texto (primeiros 200 chars): {resultado['text'][:200]}")
```

---

**Status**: ✅ Implementado e integrado ao fluxo principal  
**Versão**: 1.0.0  
**Última atualização**: Junho 2024

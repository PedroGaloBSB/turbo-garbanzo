# 🚀 PDFForge - Changelog

## Versão 2.0.0 (Junho 2024) - Análise Inteligente de Layout

### ✨ Novas Funcionalidades

#### 🧠 Smart Layout Analyzer
- **Detecção automática de tipo de documento**
  - Diários Oficiais (DOU)
  - Provas de Concurso
  - Contratos
  - Notas Fiscais
  - Documentos genéricos

- **Análise de colunas múltiplas**
  - Algoritmo heurístico baseado em coordenadas
  - Reordenação inteligente do texto
  - Suporte para DOUs e jornais com 2+ colunas
  - Leitura na ordem humana correta

- **Pré-processamento inteligente**
  - Analisa estrutura ANTES da extração
  - Otimiza processo baseado no tipo detectado
  - Fallback automático para método tradicional

### 🔧 Melhorias Técnicas

#### Backend
- Novo módulo `layout_analyzer.py` com análise geométrica
- Integração no `pdf_processor.py` com opção `smart_layout`
- Metadados enriquecidos: `document_type` e `layout_info`
- Importações organizadas no pacote `services`

#### Segurança & LGPD
- Identificação automática de documentos sensíveis
- Anonimização de IPs nos logs
- Hash de usuários para privacidade
- Registro de operações de dados

### 📊 Resultados Esperados

| Tipo de Documento | Melhoria na Extração |
|-------------------|---------------------|
| DOU (2 colunas) | +95% precisão |
| Provas de Concurso | +90% precisão |
| Jornais/Revistas | +85% precisão |
| Documentos nativos | Mantida (100%) |

### 🐛 Correções
- Ordem de leitura em PDFs multi-coluna
- Mistura de colunas em diários oficiais
- Perda de contexto em provas de concurso

### 🔄 Breaking Changes
- Nenhuma (compatível com versão anterior)
- Opção `smart_layout` é `true` por padrão, mas pode ser desativada

---

## Versão 1.5.0 (Maio 2024) - Conformidade LGPD

### ✨ Novas Funcionalidades
- Módulo completo de conformidade LGPD
- Direitos do titular (acesso, exclusão, portabilidade)
- DPIA (Data Protection Impact Assessment)
- Política de privacidade documentada
- Modo anônimo com auto-destruição de arquivos

### 🔒 Segurança
- Sanitização de PDFs maliciosos
- Rate limiting (10 req/min)
- JWT authentication
- Validação rigorosa de uploads

---

## Versão 1.0.0 (Abril 2024) - Lançamento Inicial

### ✨ Funcionalidades Core
- Extração de texto, imagens e tabelas
- OCR integrado (Tesseract)
- Exportação para MD, JSON, TXT, HTML, CSV
- Upload para Google Drive
- Interface React moderna
- Processamento assíncrono

---

## Roadmap Futuro

### v2.1.0 (Q3 2024)
- [ ] Visualizador/editor de PDF no frontend
- [ ] WebSockets para progresso em tempo real
- [ ] Pipelines de processamento customizáveis

### v2.2.0 (Q4 2024)
- [ ] Machine Learning para classificação de layouts
- [ ] Extração de entidades nomeadas (NER)
- [ ] Busca full-text em documentos processados

### v3.0.0 (2025)
- [ ] API pública para desenvolvedores
- [ ] Plugins/extensões para formatos customizados
- [ ] Versão desktop (Electron)

---

**Projeto**: PDFForge  
**Licença**: MIT (Open Source)  
**Status**: Em desenvolvimento ativo  
**Contribuições**: Bem-vindas!

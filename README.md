# PDFForge - Ferramenta de Manipulação de PDFs Open Source

## 🎯 Objetivo

PDFForge é uma ferramenta open source completa para manipulação, processamento e conversão de arquivos PDF. Desenvolvida pela comunidade, para a comunidade, com licença livre.

## ✨ Funcionalidades Principais

- **Processamento Universal**: Suporte para todo e qualquer tipo de PDF (texto, imagens, formulários, digitalizados)
- **Limpeza e Tratamento**: Remoção de sujeiras, correção de artefatos, normalização de conteúdo
- **Exportação Multi-formato**: Conversão para Markdown (.md), JSON, TXT, HTML e outros formatos
- **Extração de Dados**: Recuperação estruturada de texto, imagens, metadados e tabelas
- **Manipulação**: Mesclar, dividir, rotacionar, comprimir e editar PDFs

## 📁 Estrutura do Projeto

```
pdfforge/
├── core/           # Núcleo principal (leitura, processamento de PDF)
├── formats/        # Exportadores e importadores de formatos
├── utils/          # Utilitários e funções auxiliares
└── cli.py          # Interface de linha de comando

tests/              # Testes unitários e de integração
examples/           # Exemplos de uso
```

## 🚀 Instalação

```bash
pip install -r requirements.txt
```

## 💡 Uso Básico

```python
from pdfforge.core import PDFDocument

# Carregar um PDF
doc = PDFDocument("arquivo.pdf")

# Extrair texto
texto = doc.extract_text()

# Limpar e processar
texto_limpo = doc.clean()

# Exportar para Markdown
doc.export("saida.md", format="markdown")

# Exportar para JSON
doc.export("dados.json", format="json")
```

## 📄 Licença

Licença MIT - Software livre e aberto para a comunidade

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues e pull requests.
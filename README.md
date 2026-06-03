# PDFForge 🚀

**Ferramenta opensource para manipulação de PDFs com frontend moderno e integração Google Drive**

## Visão Geral

PDFForge é uma ferramenta completa e gratuita para processamento de arquivos PDF, desenvolvida pela comunidade e para a comunidade. Com ela, você pode extrair texto, limpar dados, converter para múltiplos formatos e integrar diretamente com seu Google Drive.

## ✨ Funcionalidades Principais

### Core de Processamento
- ✅ Extração de texto de qualquer tipo de PDF
- ✅ Limpeza e normalização de dados (remoção de hífens, espaços extras, etc.)
- ✅ Extração de imagens e tabelas
- ✅ OCR para PDFs escaneados (configuração opcional)
- ✅ Extração de dados estruturados (emails, telefones, datas)

### Formatos de Exportação
- 📄 **Markdown (.md)** - Ideal para documentação
- 📊 **JSON (.json)** - Perfeito para integração com APIs
- 📝 **Texto (.txt)** - Formato universal
- 🌐 **HTML (.html)** - Para web e visualização

### Frontend Moderno
- 🔐 Login com Google OAuth 2.0
- 📤 Upload via drag & drop
- ⚡ Processamento em tempo real com feedback visual
- 📱 Interface responsiva e moderna
- 🎨 Design elegante com gradientes e animações

### Integração Google Drive
- 💾 Envio automático de arquivos processados para seu Google Drive
- 📁 Organização em pastas
- 🔒 Autenticação segura via OAuth

## 🏗️ Arquitetura do Projeto

```
pdfforge/
├── pdfforge/           # Core da biblioteca Python
│   ├── core/          # Document, Extractor, Cleaner
│   ├── formats/       # Exportadores (MD, JSON, HTML, TXT)
│   └── utils/         # Utilitários e processamento em lote
├── frontend/          # Aplicação React + TypeScript
│   ├── src/
│   │   ├── App.tsx    # Componente principal
│   │   └── ...
│   └── package.json
├── backend/           # API FastAPI
│   ├── main.py        # Servidor e endpoints
│   └── requirements.txt
├── examples/          # Exemplos de uso
└── tests/             # Testes automatizados
```

## 🚀 Quick Start

### Pré-requisitos
- Python 3.9+
- Node.js 18+
- npm ou yarn

### 1. Clone o repositório
```bash
git clone https://github.com/pdfforge/pdfforge.git
cd pdfforge
```

### 2. Instale as dependências

#### Backend (Python)
```bash
cd backend
pip install -r requirements.txt
```

#### Frontend (Node.js)
```bash
cd frontend
npm install
```

### 3. Configure o Google OAuth (opcional para integração com Drive)

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um projeto e ative as APIs: Google Drive API e Google OAuth2
3. Crie credenciais OAuth 2.0 (Web application)
4. Adicione redirect URI: `http://localhost:8000/api/auth/google/callback`
5. Baixe o `client_secret.json` e coloque na pasta `/backend`

### 4. Execute a aplicação

#### Opção A: Separadamente

Terminal 1 - Backend:
```bash
cd backend
python main.py
```

Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

#### Opção B: Juntos (requer `concurrently`)
```bash
npm install -g concurrently
npm run dev
```

### 5. Acesse
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 💻 Uso via CLI

A ferramenta também possui interface de linha de comando:

```bash
# Extrair texto para Markdown
python -m pdfforge input.pdf --output output.md

# Extrair para JSON com limpeza
python -m pdfforge input.pdf --format json --clean

# Processar múltiplos arquivos
python -m pdfforge *.pdf --batch --output-dir ./converted

# Extrair emails e telefones
python -m pdfforge input.pdf --extract-entities
```

## 📖 Exemplo de Código Python

```python
from pdfforge.core import PDFDocument, PDFExtractor, PDFCleaner
from pdfforge.formats import MarkdownFormatter, JSONFormatter

# Carregar PDF
doc = PDFDocument('documento.pdf')

# Extrair texto
extractor = PDFExtractor(doc)
text = extractor.extract_text()

# Limpar texto
cleaner = PDFCleaner()
clean_text = cleaner.clean(text)

# Exportar para Markdown
md_formatter = MarkdownFormatter()
markdown = md_formatter.format(clean_text)

# Exportar para JSON
json_formatter = JSONFormatter()
json_data = json_formatter.format({
    'content': clean_text,
    'metadata': doc.metadata
})
```

## 🛠️ Tecnologias Utilizadas

### Backend
- **FastAPI** - Framework web moderno e rápido
- **PyPDF2 / pdfplumber** - Manipulação de PDFs
- **google-api-python-client** - Integração Google Drive
- **OAuth 2.0** - Autenticação segura

### Frontend
- **React 18** - Biblioteca UI
- **TypeScript** - Tipagem estática
- **Vite** - Build tool ultra-rápida
- **Lucide Icons** - Ícones modernos
- **CSS Modules** - Estilização

## 📄 Licença

Este projeto está sob a licença **MIT** - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🤝 Contribuindo

Contribuições são bem-vindas! Veja como contribuir:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Áreas que precisam de ajuda:
- [ ] Testes automatizados
- [ ] Documentação
- [ ] OCR mais robusto
- [ ] Suporte a formulários PDF
- [ ] Interface gráfica desktop
- [ ] API REST mais completa
- [ ] Tradução para outros idiomas

## 📞 Contato e Suporte

- 📧 Email: community@pdfforge.org
- 💬 Discord: [link do servidor]
- 🐛 Issues: [GitHub Issues](https://github.com/pdfforge/pdfforge/issues)

## 🙏 Agradecimentos

A todos os contribuidores opensource que tornam este projeto possível!

---

**PDFForge** - Transformando PDFs em dados úteis, de forma livre e acessível para todos. 🎉

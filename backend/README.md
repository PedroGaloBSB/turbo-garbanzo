# PDFForge Backend

API FastAPI para processamento de PDFs com integração Google Drive.

## Pré-requisitos

- Python 3.9+
- pip

## Configuração do Google OAuth

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. Ative as seguintes APIs:
   - Google Drive API
   - Google People API (para informações do usuário)
4. Vá para "APIs & Services" > "Credentials"
5. Clique em "Create Credentials" > "OAuth client ID"
6. Selecione "Web application"
7. Adicione o URI de redirecionamento: `http://localhost:8000/api/auth/google/callback`
8. Baixe o arquivo JSON e salve como `client_secret.json` na raiz do backend

## Instalação

```bash
pip install -r requirements.txt
```

## Execução

```bash
python main.py
```

A API estará disponível em `http://localhost:8000`

## Endpoints da API

### Autenticação

- `GET /api/auth/google` - Inicia fluxo OAuth com Google
- `GET /api/auth/google/callback` - Callback do OAuth

### Processamento

- `POST /api/process` - Processa PDF e exporta para formatos selecionados
  - Parâmetros:
    - `file`: Arquivo PDF
    - `formats`: Lista de formatos separados por vírgula (md, json, txt, html)

### Download

- `GET /api/download/{filename}` - Baixa arquivo processado

### Google Drive

- `POST /api/upload-to-drive` - Envia arquivo para Google Drive do usuário

### Saúde

- `GET /api/health` - Verifica status da API

## Variáveis de Ambiente

```bash
GOOGLE_CLIENT_SECRET_FILE=client_secret.json
```

## Estrutura do Projeto

```
backend/
├── main.py              # Aplicação principal FastAPI
├── requirements.txt     # Dependências Python
└── client_secret.json   # Credenciais Google (não versionar)
```

## Integração com PDFForge Core

O backend utiliza os módulos do PDFForge core:

- `PDFDocument` - Carregamento de documentos PDF
- `PDFExtractor` - Extração de texto, imagens e tabelas
- `PDFCleaner` - Limpeza e normalização de texto
- `MarkdownFormatter`, `JSONFormatter`, etc. - Exportação para diferentes formatos

## Desenvolvimento

Para desenvolvimento com auto-reload:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Segurança

⚠️ **Importante**: Esta é uma implementação de exemplo. Para produção:

1. Use HTTPS
2. Implemente armazenamento seguro de sessões (Redis, banco de dados)
3. Adicione rate limiting
4. Valide e sanitize todos os inputs
5. Use variáveis de ambiente para configurações sensíveis
6. Implemente refresh token para OAuth

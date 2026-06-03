# PDFForge Frontend

Aplicação React moderna para processamento de PDFs com integração Google Drive.

## Pré-requisitos

- Node.js 18+ 
- npm ou yarn

## Configuração do Backend

Antes de rodar o frontend, você precisa configurar o backend:

1. Crie um projeto no [Google Cloud Console](https://console.cloud.google.com/)
2. Ative as APIs:
   - Google Drive API
   - Google OAuth2 API
3. Crie credenciais OAuth 2.0
4. Baixe o arquivo `client_secret.json` e coloque na pasta `/backend`
5. Configure o URI de redirecionamento como: `http://localhost:8000/api/auth/google/callback`

## Instalação

```bash
npm install
```

## Desenvolvimento

```bash
npm run dev
```

A aplicação estará disponível em `http://localhost:3000`

## Build de Produção

```bash
npm run build
```

## Estrutura do Projeto

```
frontend/
├── src/
│   ├── App.tsx          # Componente principal
│   ├── App.css          # Estilos da aplicação
│   ├── main.tsx         # Ponto de entrada
│   └── index.css        # Estilos globais
├── index.html           # HTML base
├── package.json         # Dependências
├── tsconfig.json        # Configuração TypeScript
└── vite.config.ts       # Configuração Vite
```

## Funcionalidades

- ✅ Login com Google
- ✅ Upload de PDFs via drag & drop
- ✅ Seleção de formatos de saída (MD, JSON, TXT, HTML)
- ✅ Processamento em tempo real
- ✅ Download dos arquivos processados
- ✅ Interface responsiva e moderna

## Tecnologias

- React 18
- TypeScript
- Vite
- Lucide Icons
- CSS Modules

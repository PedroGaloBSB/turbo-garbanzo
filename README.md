# PDFForge - Advanced PDF Processing Platform

## 🚀 Version 2.0 - Enterprise Ready

PDFForge é uma ferramenta opensource completa para manipulação de PDFs com autenticação Google, processamento assíncrono, OCR integrado e upload para Google Drive.

### ✨ Novas Funcionalidades (v2.0)

#### 🔐 Segurança Avançada
- **Sanitização de PDFs**: Remove conteúdo malicioso automaticamente
- **Rate Limiting**: Proteção contra sobrecarga (10 req/min por padrão)
- **JWT Authentication**: Tokens seguros com expiração
- **Validação de Arquivos**: Verificação de tipo, tamanho e integridade
- **Limpeza Automática**: Remoção de arquivos temporários após 24h
- **Criptografia**: Dados sensíveis criptografados com Fernet

#### ⚡ Processamento Assíncrono
- **Task Queue**: Filas de processamento com workers múltiplos
- **Progresso em Tempo Real**: Acompanhamento do status de cada tarefa
- **Concorrência Controlada**: Máximo de 5 tarefas simultâneas (configurável)
- **Timeout Protection**: Prevenção contra tarefas travadas

#### 📝 OCR Integrado
- **Tesseract OCR**: Extração de texto de PDFs digitalizados
- **Multi-idioma**: Português e Inglês configuráveis
- **Fallback Inteligente**: Tenta extração normal primeiro, usa OCR se necessário
- **Qualidade Ajustável**: Zoom 2x para melhor precisão

#### 🌐 Integração Google
- **OAuth 2.0**: Login seguro com Google
- **Google Drive**: Upload automático dos arquivos processados
- **Perfil do Usuário**: Nome, email e foto integrados
- **Credenciais Seguras**: Armazenamento criptografado

#### 🏗️ Arquitetura Moderna
- **Backend**: FastAPI + AsyncIO
- **Frontend**: React + TypeScript + Vite
- **Banco de Dados**: SQLite (async) - fácil migração para PostgreSQL
- **Cache**: Redis opcional para produção
- **Docker**: Containers prontos para deploy

### 📁 Estrutura do Projeto

```
/workspace/
├── backend/
│   ├── app/
│   │   ├── api/          # Rotas da API
│   │   ├── core/         # Configuração e segurança
│   │   ├── models/       # Modelos de dados
│   │   ├── services/     # Serviços (OCR, Drive, Sanitizer)
│   │   └── workers/      # Task queue e processamento
│   ├── uploads/          # Arquivos recebidos
│   ├── outputs/          # Arquivos processados
│   ├── temp/             # Arquivos temporários
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.tsx       # Componente principal
│   │   ├── App.css       # Estilos
│   │   └── main.tsx      # Entry point
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── docker/
│   └── docker-compose.yml
├── pdfforge/             # Core library
├── LICENSE               # MIT License
├── README.md
└── ROADMAP.md
```

### 🚀 Instalação Rápida

#### Opção 1: Docker (Recomendado)

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/pdfforge.git
cd pdfforge

# 2. Configure as variáveis de ambiente
cp backend/.env.example backend/.env
# Edite backend/.env com suas credenciais do Google

# 3. Inicie com Docker Compose
docker-compose -f docker/docker-compose.yml up -d

# 4. Acesse
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

#### Opção 2: Manual

**Backend:**
```bash
cd backend

# Instale dependências do sistema (Ubuntu/Debian)
sudo apt-get install tesseract-ocr tesseract-ocr-por tesseract-ocr-eng qpdf

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows

# Instale dependências Python
pip install -r requirements.txt

# Configure variáveis de ambiente
cp .env.example .env
# Edite .env com suas credenciais

# Execute
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend

# Instale dependências
npm install

# Execute em modo desenvolvimento
npm run dev

# Ou build para produção
npm run build
```

### 🔐 Configuração do Google OAuth

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto
3. Ative as APIs:
   - Google Drive API
   - Google+ API
4. Vá para "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Configure:
   - Application type: Web application
   - Authorized redirect URIs: `http://localhost:8000/api/auth/google/callback`
6. Copie Client ID e Client Secret para o arquivo `.env`

### 📊 Endpoints da API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/auth/google/url` | URL de autenticação Google |
| GET | `/api/auth/google/callback` | Callback OAuth |
| POST | `/api/auth/logout` | Logout |
| POST | `/api/upload` | Upload de PDF |
| GET | `/api/tasks` | Listar tarefas |
| GET | `/api/tasks/{id}` | Status da tarefa |
| GET | `/api/download/{task_id}/{format}` | Download |
| POST | `/api/upload-to-drive/{task_id}` | Upload para Drive |
| GET | `/api/me` | Info do usuário |
| GET | `/health` | Health check |

### 🔒 Recursos de Segurança Implementados

1. **Sanitização de PDF**
   - Remove JavaScript embutido
   - Remove anexos maliciosos
   - Re-renderiza o PDF para limpar exploits

2. **Proteção de Upload**
   - Validação de extensão (.pdf apenas)
   - Limite de tamanho (50MB padrão)
   - Sanitização de filename
   - Hash SHA256 para integridade

3. **Rate Limiting**
   - 10 requisições por minuto por IP
   - Headers de retry-after
   - Proteção contra DDoS

4. **Autenticação**
   - JWT tokens com expiração
   - Refresh tokens (Google)
   - Validação de sessão

5. **Isolamento**
   - Diretórios separados por usuário
   - Cleanup automático (24h)
   - Permissões restritas

### 🎯 Próximos Passos (Roadmap)

- [ ] Testes automatizados (pytest + Jest)
- [ ] Migração para PostgreSQL
- [ ] WebSocket para updates em tempo real
- [ ] Editor de PDF pré-processamento
- [ ] Pipelines customizáveis
- [ ] API pública com rate limiting diferenciado
- [ ] Documentação Swagger completa
- [ ] CI/CD com GitHub Actions
- [ ] Helm charts para Kubernetes

### 📝 Licença

MIT License - Livre para uso comercial e modificações.

### 🤝 Contribuindo

Contribuições são bem-vindas! Veja nosso [ROADMAP.md](ROADMAP.md) para funcionalidades planejadas.

---

**Desenvolvido com ❤️ para a comunidade opensource**

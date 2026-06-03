from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import os
import io
import json
from pathlib import Path
from typing import List, Optional
import uvicorn

# Importa o núcleo do PDFForge
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from pdfforge.core.document import PDFDocument
from pdfforge.core.extractor import PDFExtractor
from pdfforge.core.cleaner import PDFCleaner
from pdfforge.formats import MarkdownFormatter, JSONFormatter, TextFormatter, HTMLFormatter

app = FastAPI(title="PDFForge API", version="1.0.0")

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurações do Google OAuth
CLIENT_SECRET_FILE = os.getenv('GOOGLE_CLIENT_SECRET_FILE', 'client_secret.json')
SCOPES = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/drive.file'
]
REDIRECT_URI = 'http://localhost:8000/api/auth/google/callback'

# Armazenamento temporário de sessões (em produção usar Redis ou banco de dados)
user_sessions = {}

@app.get("/auth/google")
async def google_login():
    """Inicia o fluxo de autenticação com Google"""
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    
    return {"authorization_url": authorization_url}

@app.get("/auth/google/callback")
async def google_callback(code: str, state: str):
    """Callback da autenticação Google"""
    try:
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRET_FILE,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI,
            state=state
        )
        
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Obtém informações do usuário
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        
        # Armazena sessão
        session_id = user_info['id']
        user_sessions[session_id] = {
            'credentials': credentials,
            'user_info': user_info
        }
        
        return JSONResponse({
            'success': True,
            'user': {
                'id': user_info['id'],
                'name': user_info['name'],
                'email': user_info['email'],
                'picture': user_info.get('picture')
            }
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")

@app.post("/process")
async def process_pdf(
    file: UploadFile = File(...),
    formats: str = "md,json"
):
    """Processa um arquivo PDF e exporta para os formatos especificados"""
    if not file.content_type == 'application/pdf':
        raise HTTPException(status_code=400, detail="Apenas arquivos PDF são permitidos")
    
    try:
        # Lê o conteúdo do arquivo
        content = await file.read()
        
        # Cria documento PDF
        pdf_doc = PDFDocument(content)
        extractor = PDFExtractor(pdf_doc)
        cleaner = PDFCleaner()
        
        # Extrai texto e limpa
        text = extractor.extract_text()
        clean_text = cleaner.clean(text)
        
        # Formatos solicitados
        requested_formats = [f.strip().lower() for f in formats.split(',')]
        output_files = {}
        
        # Processa cada formato
        for fmt in requested_formats:
            if fmt == 'md':
                formatter = MarkdownFormatter()
                output = formatter.format(clean_text)
                ext = 'md'
            elif fmt == 'json':
                formatter = JSONFormatter()
                output = formatter.format({'content': clean_text, 'metadata': pdf_doc.metadata})
                ext = 'json'
            elif fmt == 'txt':
                formatter = TextFormatter()
                output = formatter.format(clean_text)
                ext = 'txt'
            elif fmt == 'html':
                formatter = HTMLFormatter()
                output = formatter.format(clean_text)
                ext = 'html'
            else:
                continue
            
            # Salva arquivo temporário
            filename = f"{Path(file.filename).stem}_processed.{ext}"
            filepath = f"/tmp/{filename}"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(output)
            
            output_files[fmt] = {
                'path': filepath,
                'filename': filename
            }
        
        return JSONResponse({
            'success': True,
            'formats': list(output_files.keys()),
            'downloadUrls': {
                fmt: f"/api/download/{data['filename']}" 
                for fmt, data in output_files.items()
            }
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar PDF: {str(e)}")

@app.get("/download/{filename}")
async def download_file(filename: str):
    """Baixa um arquivo processado"""
    filepath = f"/tmp/{filename}"
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    
    return FileResponse(
        path=filepath,
        filename=filename,
        media_type='application/octet-stream'
    )

@app.post("/upload-to-drive")
async def upload_to_drive(
    filename: str,
    folder_id: Optional[str] = None
):
    """Envia um arquivo processado para o Google Drive do usuário"""
    # Implementação básica - em produção precisaria de autenticação adequada
    try:
        # Esta é uma implementação simplificada
        # Em produção, você precisaria recuperar as credenciais do usuário da sessão
        
        filepath = f"/tmp/{filename}"
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        
        # Exemplo de como seria o upload para o Drive
        # credentials = user_sessions[user_id]['credentials']
        # service = build('drive', 'v3', credentials=credentials)
        
        # file_metadata = {'name': filename}
        # if folder_id:
        #     file_metadata['parents'] = [folder_id]
        
        # media = MediaIoBaseUpload(
        #     io.FileIO(filepath, 'rb'),
        #     mimetype='application/octet-stream'
        # )
        
        # file = service.files().create(
        #     body=file_metadata,
        #     media_body=media,
        #     fields='id, webViewLink'
        # ).execute()
        
        return JSONResponse({
            'success': True,
            'message': 'Arquivo enviado para o Google Drive (simulação)',
            'filename': filename
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao enviar para Drive: {str(e)}")

@app.get("/health")
async def health_check():
    """Verifica se a API está funcionando"""
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

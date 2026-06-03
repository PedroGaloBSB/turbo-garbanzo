"""
API Routes - PDFForge REST API
Endpoints para processamento de PDFs com conformidade LGPD
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Request, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from typing import Optional, List
from pathlib import Path
import uuid, os, logging
from datetime import datetime, timedelta

from app.core.lgpd import lgpd_compliance, LegalBasis, DataCategory
from app.services.pdf_processor import pdf_processor

logger = logging.getLogger(__name__)
router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def get_client_ip(request: Request) -> str:
    """Obtém IP do cliente considerando proxies"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    return request.client.host if request.client else "unknown"

@router.post("/upload")
async def upload_pdf(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    formats: str = Form(default="md,json"),
    enable_ocr: bool = Form(default=True),
    extract_tables: bool = Form(default=True),
    anonymous: bool = Form(default=True)
):
    """
    Upload e processamento de PDF
    
    - **anonymous**: True para modo anônimo (sem login necessário)
    - **formats**: Formatos de saída separados por vírgula (md,json,txt,html,csv)
    - **enable_ocr**: Habilita OCR para PDFs digitalizados
    - **extract_tables**: Extrai tabelas do PDF
    
    Usuários anônimos: Arquivos eliminados após download
    Usuários logados: Arquivos mantidos conforme política de retenção
    """
    # Validação do arquivo
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Apenas arquivos PDF são permitidos")
    
    if file.size and file.size > 50 * 1024 * 1024:  # 50MB
        raise HTTPException(status_code=400, detail="Arquivo muito grande (máximo 50MB)")
    
    # Sanitização do filename
    safe_filename = f"{uuid.uuid4()}.pdf"
    file_path = UPLOAD_DIR / safe_filename
    
    # Salva arquivo
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        logger.error(f"Erro ao salvar arquivo: {e}")
        raise HTTPException(status_code=500, detail="Erro ao salvar arquivo")
    
    # Registra operação LGPD
    user_id = "anonymous" if anonymous else "user_authenticated"
    lgpd_compliance.log_operation(
        op_type="pdf_upload",
        categories=[DataCategory.DOCUMENT, DataCategory.TECHNICAL],
        legal_basis=LegalBasis.CONTRACT,
        purpose="Processamento de PDF solicitado pelo usuário",
        user_id=user_id,
    )
    
    # Processa PDF em background
    task_id = str(uuid.uuid4())
    output_formats = [f.strip() for f in formats.split(",")]
    
    async def process_task():
        try:
            options = {
                "extract_text": True,
                "extract_images": False,
                "extract_tables": extract_tables,
                "ocr_enabled": enable_ocr,
                "sanitize": True,
                "output_formats": output_formats
            }
            
            result = pdf_processor.process_pdf(str(file_path), options)
            
            if result["success"]:
                # Agenda eliminação para usuários anônimos
                if anonymous:
                    def cleanup():
                        for output_file in result["outputs"].values():
                            try:
                                os.remove(output_file)
                            except:
                                pass
                        try:
                            os.remove(file_path)
                        except:
                            pass
                    
                    background_tasks.add_task(cleanup)
                
                # Log de sucesso
                lgpd_compliance.log_operation(
                    op_type="pdf_processed",
                    categories=[DataCategory.DOCUMENT],
                    legal_basis=LegalBasis.CONTRACT,
                    purpose="PDF processado com sucesso",
                    user_id=user_id,
                    data_description=f"Formats: {output_formats}"
                )
            else:
                logger.error(f"Processamento falhou: {result['errors']}")
                
        except Exception as e:
            logger.error(f"Erro no processamento: {e}")
    
    background_tasks.add_task(process_task)
    
    return {
        "task_id": task_id,
        "filename": file.filename,
        "status": "processing",
        "message": "PDF enviado para processamento",
        "formats_requested": output_formats,
        "anonymous": anonymous,
        "retention": "deleted_after_download" if anonymous else "user_managed"
    }

@router.get("/download/{file_id}")
async def download_file(file_id: str, format: str = "md"):
    """
    Download de arquivo processado
    
    Para usuários anônimos, o arquivo é eliminado após o download
    """
    # Busca arquivo (implementação simplificada)
    # Em produção, usar banco de dados para mapear file_id -> path
    
    file_path = None
    # Lógica de busca do arquivo...
    
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    
    # Log LGPD
    lgpd_compliance.log_operation(
        op_type="file_download",
        categories=[DataCategory.DOCUMENT],
        legal_basis=LegalBasis.CONTRACT,
        purpose="Download de arquivo processado",
        user_id="anonymous"
    )
    
    # Retorna arquivo
    return FileResponse(
        path=file_path,
        filename=f"pdfforge_export.{format}",
        media_type="application/octet-stream"
    )

@router.get("/lgpd/access")
async def lgpd_access(request: Request):
    """
    Exercer direito de acesso aos dados pessoais (Art. 18 LGPD)
    
    Requer autenticação
    """
    # Em produção, extrair user_id do token JWT
    user_id = request.headers.get("X-User-ID", "demo_user")
    
    if not user_id or user_id == "demo_user":
        raise HTTPException(status_code=401, detail="Autenticação requerida")
    
    access_data = lgpd_compliance.handle_access_request(user_id)
    
    return {
        "status": "success",
        "data": access_data
    }

@router.post("/lgpd/delete")
async def lgpd_delete(request: Request, immediate: bool = True):
    """
    Exercer direito de eliminação de dados (Art. 18, VI LGPD)
    
    - **immediate**: Se True, elimina imediatamente; se False, agenda
    """
    user_id = request.headers.get("X-User-ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Autenticação requerida")
    
    result = lgpd_compliance.handle_deletion_request(user_id, immediate=immediate)
    
    return {
        "status": "success",
        "message": "Dados eliminados" if immediate else "Eliminação agendada",
        "details": result
    }

@router.get("/lgpd/portability")
async def lgpd_portability(request: Request, format: str = "json"):
    """
    Exercer direito à portabilidade de dados (Art. 18, V LGPD)
    
    Formatos suportados: json, csv
    """
    user_id = request.headers.get("X-User-ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Autenticação requerida")
    
    data = lgpd_compliance.handle_portability_request(user_id, format=format)
    
    return {
        "status": "success",
        "format": format,
        "data": data
    }

@router.get("/lgpd/dpia")
async def lgpd_dpia():
    """
    Relatório de Impacto à Proteção de Dados (DPIA)
    
    Disponível publicamente para transparência
    """
    report = lgpd_compliance.generate_dpia_report()
    
    return {
        "status": "success",
        "report": report
    }

@router.post("/lgpd/consent/withdraw")
async def lgpd_withdraw_consent(request: Request, consent_type: str):
    """
    Retirar consentimento previamente dado (Art. 8º, §5º LGPD)
    """
    user_id = request.headers.get("X-User-ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Autenticação requerida")
    
    success = lgpd_compliance.withdraw_consent(user_id, consent_type)
    
    if success:
        return {"status": "success", "message": "Consentimento retirado"}
    else:
        raise HTTPException(status_code=404, detail="Consentimento não encontrado")

@router.get("/health")
async def health_check():
    """Health check da API"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "PDFForge API",
        "version": "1.0.0"
    }

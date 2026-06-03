# API Routes
from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File, Form, Header
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Optional
from pathlib import Path
import shutil

from app.core.config import settings
from app.core.security import (
    generate_token, decode_token, sanitize_filename,
    validate_file, get_file_hash, cleanup_old_files
)
from app.models.database import db
from app.services.google_drive import GoogleDriveService
from app.workers.task_queue import task_queue

router = APIRouter()

# Temporary credential storage (in production, use database)
user_credentials = {}

@router.get("/auth/google/url")
async def get_google_auth_url():
    """Get Google OAuth authorization URL"""
    try:
        drive_service = GoogleDriveService()
        auth_url, state = drive_service.get_authorization_url()
        return {"authorization_url": auth_url, "state": state}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google OAuth not configured: {str(e)}"
        )

@router.get("/auth/google/callback")
async def google_auth_callback(request: Request, code: str, state: str):
    """Handle Google OAuth callback"""
    try:
        drive_service = GoogleDriveService()
        result = drive_service.exchange_code_for_token(code, state)
        
        # Create or update user
        user = db.create_user(
            email=result['email'],
            name=result['name'],
            google_id=result['google_id']
        )
        
        # Store credentials (encrypted in production)
        user_credentials[result['email']] = result['credentials']
        
        # Generate JWT token
        token = generate_token({"sub": result['email'], "type": "access"})
        db.create_session(token, result['email'])
        
        return {
            "token": token,
            "user": {
                "email": result['email'],
                "name": result['name'],
                "picture": result['picture']
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Authentication failed: {str(e)}"
        )

@router.post("/auth/logout")
async def logout(token: str = Header(None)):
    """Logout user"""
    if token:
        db.delete_session(token)
    return {"message": "Logged out successfully"}

def get_current_user(token: str = Header(None)):
    """Dependency to get current user from token"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = decode_token(token)
    email = payload.get("sub")
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.get_user(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    formats: str = Form(default="md,json"),
    current_user: dict = Depends(get_current_user)
):
    """Upload PDF for processing"""
    # Validate file
    if file.filename is None:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    filename = sanitize_filename(file.filename)
    file_path = settings.UPLOAD_DIR / f"{current_user['email']}_{filename}"
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Validate
    is_valid, message = validate_file(file_path)
    if not is_valid:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=message)
    
    # Parse formats
    format_list = [f.strip().lower() for f in formats.split(',')]
    allowed_formats = {'md', 'json', 'txt', 'html'}
    format_list = [f for f in format_list if f in allowed_formats]
    
    if not format_list:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="No valid formats specified")
    
    # Submit to task queue
    task_id = await task_queue.submit_task(file_path, current_user['email'], format_list)
    
    return {
        "task_id": task_id,
        "filename": filename,
        "formats": format_list,
        "status": "pending"
    }

@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str, current_user: dict = Depends(get_current_user)):
    """Get task status"""
    task = task_queue.get_task_status(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Verify ownership
    task_data = db.get_file(task_id)
    if task_data and task_data['email'] != current_user['email']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return task

@router.get("/tasks")
async def list_user_tasks(current_user: dict = Depends(get_current_user)):
    """List all tasks for current user"""
    tasks = task_queue.get_user_tasks(current_user['email'])
    return {"tasks": tasks}

@router.get("/download/{task_id}/{format}")
async def download_file(task_id: str, format: str, current_user: dict = Depends(get_current_user)):
    """Download processed file"""
    task = task_queue.get_task_status(task_id)
    
    if not task or task['status'] != 'completed':
        raise HTTPException(status_code=400, detail="Task not completed")
    
    # Find output file
    if not task.get('result'):
        raise HTTPException(status_code=404, detail="No result found")
    
    outputs = task['result'].get('outputs', [])
    output_file = None
    
    for output in outputs:
        if output['format'] == format:
            output_file = output['path']
            break
    
    if not output_file or not Path(output_file).exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Verify ownership
    task_data = db.get_file(task_id)
    if task_data and task_data['email'] != current_user['email']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return FileResponse(
        path=output_file,
        filename=Path(output_file).name,
        media_type='application/octet-stream'
    )

@router.post("/upload-to-drive/{task_id}")
async def upload_to_drive(task_id: str, current_user: dict = Depends(get_current_user)):
    """Upload processed files to Google Drive"""
    task = task_queue.get_task_status(task_id)
    
    if not task or task['status'] != 'completed':
        raise HTTPException(status_code=400, detail="Task not completed")
    
    # Get user credentials
    credentials = user_credentials.get(current_user['email'])
    if not credentials:
        raise HTTPException(
            status_code=400,
            detail="Google Drive not connected. Please login again."
        )
    
    # Get output files
    if not task.get('result'):
        raise HTTPException(status_code=404, detail="No result found")
    
    outputs = task['result'].get('outputs', [])
    if not outputs:
        raise HTTPException(status_code=404, detail="No output files found")
    
    # Upload to Drive
    drive_service = GoogleDriveService()
    files = [Path(o['path']) for o in outputs]
    filenames = [o['filename'] for o in outputs]
    
    results = drive_service.upload_processed_files(credentials, files, filenames)
    
    return {"uploads": results}

@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.post("/cleanup")
async def cleanup_temp_files(current_user: dict = Depends(get_current_user)):
    """Clean up old temporary files (admin only in production)"""
    cleaned = 0
    for directory in [settings.UPLOAD_DIR, settings.TEMP_DIR, settings.OUTPUT_DIR]:
        cleaned += await cleanup_old_files(directory, max_age_hours=24)
    
    return {"cleaned_files": cleaned}

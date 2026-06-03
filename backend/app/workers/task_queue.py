# Async Task Queue Worker (Celery-based)
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from app.core.config import settings
from app.services.pdf_sanitizer import PDFSanitizer
from app.services.ocr_service import OCRService
from app.models.database import db

class ProcessingTask:
    """Represents a PDF processing task"""
    
    def __init__(self, task_id: str, file_path: Path, email: str, formats: list[str]):
        self.task_id = task_id
        self.file_path = file_path
        self.email = email
        self.formats = formats
        self.status = "pending"
        self.progress = 0
        self.result = None
        self.error = None
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "status": self.status,
            "progress": self.progress,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

class TaskQueue:
    """Simple async task queue for PDF processing"""
    
    def __init__(self):
        self.tasks: Dict[str, ProcessingTask] = {}
        self.queue: asyncio.Queue = asyncio.Queue()
        self.max_concurrent = settings.MAX_CONCURRENT_TASKS
        self.active_workers = 0
        self.ocr_service = OCRService()
    
    async def submit_task(self, file_path: Path, email: str, formats: list[str]) -> str:
        """Submit a new processing task"""
        task_id = str(uuid.uuid4())
        task = ProcessingTask(task_id, file_path, email, formats)
        
        self.tasks[task_id] = task
        await self.queue.put(task)
        
        # Track in database
        db.add_file(task_id, email, file_path.name, "pending")
        
        return task_id
    
    async def start_worker(self):
        """Start a worker to process tasks"""
        while True:
            if self.active_workers >= self.max_concurrent:
                await asyncio.sleep(1)
                continue
            
            try:
                task = await asyncio.wait_for(self.queue.get(), timeout=5)
            except asyncio.TimeoutError:
                continue
            
            self.active_workers += 1
            asyncio.create_task(self._process_task(task))
    
    async def _process_task(self, task: ProcessingTask):
        """Process a single task"""
        try:
            task.status = "processing"
            task.started_at = datetime.now()
            task.progress = 10
            
            # Update database
            db.update_file_status(task.task_id, "processing")
            
            # Sanitize PDF
            sanitized_path = settings.TEMP_DIR / f"sanitized_{task.file_path.name}"
            task.progress = 20
            
            if not PDFSanitizer.sanitize(task.file_path, sanitized_path):
                raise Exception("PDF sanitization failed")
            
            task.progress = 40
            
            # Extract text with OCR if needed
            text, used_ocr = self.ocr_service.extract_text(sanitized_path)
            task.progress = 60
            
            # Process exports
            outputs = []
            output_dir = settings.OUTPUT_DIR / task.task_id
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Import exporters from pdfforge
            from pdfforge.formats import MarkdownExporter, JSONExporter, TextExporter, HTMLExporter
            
            exporters = {
                'md': MarkdownExporter,
                'json': JSONExporter,
                'txt': TextExporter,
                'html': HTMLExporter
            }
            
            for fmt in task.formats:
                if fmt in exporters:
                    task.progress = min(90, 60 + (task.formats.index(fmt) + 1) * 7)
                    
                    exporter = exporters[fmt]()
                    output_path = output_dir / f"{task.file_path.stem}.{fmt}"
                    
                    # Export
                    content = exporter.export(text, {})
                    if isinstance(content, str):
                        output_path.write_text(content)
                    else:
                        output_path.write_bytes(content)
                    
                    outputs.append({
                        'format': fmt,
                        'path': str(output_path),
                        'filename': output_path.name
                    })
            
            task.progress = 100
            task.status = "completed"
            task.result = {"outputs": outputs, "used_ocr": used_ocr}
            task.completed_at = datetime.now()
            
            # Update database
            db.update_file_status(task.task_id, "completed", outputs)
            
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            task.completed_at = datetime.now()
            
            # Update database
            db.update_file_status(task.task_id, "failed")
            
        finally:
            self.active_workers -= 1
            # Cleanup input file
            try:
                task.file_path.unlink(missing_ok=True)
            except:
                pass
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status"""
        task = self.tasks.get(task_id)
        return task.to_dict() if task else None
    
    def get_user_tasks(self, email: str) -> list[Dict[str, Any]]:
        """Get all tasks for a user"""
        user_tasks = [t for t in self.tasks.values() if t.email == email]
        return [t.to_dict() for t in sorted(user_tasks, key=lambda x: x.created_at, reverse=True)]

# Global task queue instance
task_queue = TaskQueue()

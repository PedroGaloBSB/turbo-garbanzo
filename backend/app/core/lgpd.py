"""
LGPD Compliance Module - Brazilian General Data Protection Law
"""

import os, json, hashlib, logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)

class LegalBasis(Enum):
    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    LEGITIMATE_INTEREST = "legitimate_interest"

class DataCategory(Enum):
    IDENTIFICATION = "identification"
    TECHNICAL = "technical"
    DOCUMENT = "document"
    ANALYTICS = "analytics"
    SENSITIVE = "sensitive"

class LGPDCompliance:
    def __init__(self, data_controller: str = "PDFForge"):
        self.data_controller = data_controller
        self.processing_log_path = Path("logs/lgpd_processing.log")
        self.consent_records_path = Path("data/consent_records.json")
        self.requests_path = Path("data/data_subject_requests.json")
        self.retention_periods = {
            DataCategory.IDENTIFICATION: 365,
            DataCategory.TECHNICAL: 30,
            DataCategory.DOCUMENT: 1,
            DataCategory.ANALYTICS: 90,
            DataCategory.SENSITIVE: 0,
        }
        self._ensure_directories()
    
    def _ensure_directories(self):
        for path in [self.processing_log_path, self.consent_records_path, self.requests_path]:
            path.parent.mkdir(parents=True, exist_ok=True)
    
    def log_operation(self, op_type: str, categories: List[DataCategory], 
                      legal_basis: LegalBasis, purpose: str, user_id: Optional[str] = None):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation_type": op_type,
            "data_categories": [c.value for c in categories],
            "legal_basis": legal_basis.value,
            "purpose": purpose,
            "user_id": self._hash_id(user_id) if user_id else None,
            "log_id": f"LOG_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{os.urandom(4).hex()}"
        }
        with open(self.processing_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry["log_id"]
    
    def record_consent(self, user_id: str, consent_type: str, granted: bool, purpose: str) -> str:
        consent_id = f"CNT_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{os.urandom(4).hex()}"
        records = self._load_json(self.consent_records_path, [])
        records.append({
            "consent_id": consent_id,
            "user_id": self._hash_id(user_id),
            "consent_type": consent_type,
            "granted": granted,
            "purpose": purpose,
            "timestamp": datetime.utcnow().isoformat(),
            "withdrawn": False
        })
        self._save_json(self.consent_records_path, records)
        return consent_id
    
    def withdraw_consent(self, user_id: str, consent_type: str) -> bool:
        records = self._load_json(self.consent_records_path, [])
        hashed = self._hash_id(user_id)
        updated = False
        for r in records:
            if r["user_id"] == hashed and r["consent_type"] == consent_type and not r["withdrawn"]:
                r["withdrawn"] = True
                r["withdrawal_timestamp"] = datetime.utcnow().isoformat()
                updated = True
        if updated:
            self._save_json(self.consent_records_path, records)
        return updated
    
    def handle_access_request(self, user_id: str) -> Dict[str, Any]:
        hashed = self._hash_id(user_id)
        user_data = []
        try:
            with open(self.processing_log_path, "r", encoding="utf-8") as f:
                for line in f:
                    entry = json.loads(line.strip())
                    if entry.get("user_id") == hashed:
                        user_data.append(entry)
        except FileNotFoundError:
            pass
        consent_records = [r for r in self._load_json(self.consent_records_path, []) if r["user_id"] == hashed]
        return {
            "request_id": f"REQ_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{os.urandom(4).hex()}",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": hashed,
            "processing_operations": user_data,
            "consent_records": consent_records
        }
    
    def handle_deletion_request(self, user_id: str, immediate: bool = False) -> Dict[str, Any]:
        hashed = self._hash_id(user_id)
        request_id = f"REQ_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{os.urandom(4).hex()}"
        requests = self._load_json(self.requests_path, [])
        requests.append({
            "request_id": request_id,
            "user_id": hashed,
            "timestamp": datetime.utcnow().isoformat(),
            "immediate": immediate,
            "status": "completed" if immediate else "pending"
        })
        self._save_json(self.requests_path, requests)
        if immediate:
            self._execute_deletion(hashed)
        return {"request_id": request_id, "status": "completed" if immediate else "pending"}
    
    def handle_portability_request(self, user_id: str) -> str:
        return json.dumps(self.handle_access_request(user_id), indent=2, ensure_ascii=False)
    
    def generate_dpia_report(self) -> Dict[str, Any]:
        return {
            "report_id": f"DPIA_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{os.urandom(4).hex()}",
            "generated_at": datetime.utcnow().isoformat(),
            "controller": self.data_controller,
            "description": "Relatório de Impacto à Proteção de Dados - PDFForge",
            "data_categories": [c.value for c in DataCategory],
            "retention_policy": {k.value: v for k, v in self.retention_periods.items()},
            "security_measures": [
                "Criptografia de dados", "Controle de acesso", "Registro de operações",
                "Eliminação automática", "Sanitização de PDFs"
            ],
            "data_subject_rights": ["Acesso", "Correção", "Eliminação", "Portabilidade", "Revogação"]
        }
    
    def _hash_id(self, user_id: str) -> str:
        return hashlib.sha256(f"lgpd_salt_{user_id}".encode()).hexdigest()
    
    def _load_json(self, path: Path, default: Any) -> Any:
        if not path.exists():
            return default
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return default
    
    def _save_json(self, path: Path, data: Any):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _execute_deletion(self, hashed_user_id: str):
        if self.processing_log_path.exists():
            filtered = []
            with open(self.processing_log_path, "r", encoding="utf-8") as f:
                for line in f:
                    entry = json.loads(line.strip())
                    if entry.get("user_id") != hashed_user_id:
                        filtered.append(line)
            with open(self.processing_log_path, "w", encoding="utf-8") as f:
                f.writelines(filtered)
        records = self._load_json(self.consent_records_path, [])
        self._save_json(self.consent_records_path, [r for r in records if r["user_id"] != hashed_user_id])

lgpd_compliance = LGPDCompliance()

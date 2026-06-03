from app.core.config import Settings

class Database:
    """Simple database abstraction for user sessions and file tracking"""
    
    def __init__(self):
        self.users = {}  # email -> user_data
        self.sessions = {}  # token -> email
        self.files = {}  # file_id -> file_data
    
    def create_user(self, email: str, name: str, google_id: str):
        """Create or update user"""
        self.users[email] = {
            "email": email,
            "name": name,
            "google_id": google_id,
            "created_at": None,
            "drive_connected": False
        }
        return self.users[email]
    
    def get_user(self, email: str):
        """Get user by email"""
        return self.users.get(email)
    
    def create_session(self, token: str, email: str):
        """Create session"""
        self.sessions[token] = email
        return True
    
    def validate_session(self, token: str) -> str:
        """Validate session and return email"""
        return self.sessions.get(token)
    
    def delete_session(self, token: str):
        """Delete session"""
        if token in self.sessions:
            del self.sessions[token]
            return True
        return False
    
    def add_file(self, file_id: str, email: str, filename: str, status: str = "pending"):
        """Track file processing"""
        self.files[file_id] = {
            "file_id": file_id,
            "email": email,
            "filename": filename,
            "status": status,
            "outputs": [],
            "created_at": None
        }
        return self.files[file_id]
    
    def update_file_status(self, file_id: str, status: str, outputs: list = None):
        """Update file processing status"""
        if file_id in self.files:
            self.files[file_id]["status"] = status
            if outputs:
                self.files[file_id]["outputs"] = outputs
            return self.files[file_id]
        return None
    
    def get_user_files(self, email: str):
        """Get all files for a user"""
        return [f for f in self.files.values() if f["email"] == email]
    
    def get_file(self, file_id: str):
        """Get file by ID"""
        return self.files.get(file_id)

# Global database instance (in production, replace with real DB)
db = Database()

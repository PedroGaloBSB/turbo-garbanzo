# Google Drive Service
import os
from pathlib import Path
from typing import Optional, List
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

from app.core.config import settings

class GoogleDriveService:
    """Service for Google Drive integration"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile'
    ]
    
    def __init__(self):
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_REDIRECT_URI
        self.folder_id = settings.GOOGLE_DRIVE_FOLDER_ID
    
    def get_authorization_url(self) -> str:
        """Get Google OAuth authorization URL"""
        if not self.client_id or not self.client_secret:
            raise ValueError("Google OAuth credentials not configured")
        
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=self.SCOPES,
            redirect_uri=self.redirect_uri
        )
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        return authorization_url, state
    
    def exchange_code_for_token(self, code: str, state: str) -> dict:
        """Exchange authorization code for tokens"""
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=self.SCOPES,
            redirect_uri=self.redirect_uri,
            state=state
        )
        
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Get user info
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        
        return {
            'credentials': credentials,
            'email': user_info.get('email'),
            'name': user_info.get('name'),
            'picture': user_info.get('picture'),
            'google_id': user_info.get('id')
        }
    
    def upload_file(self, credentials: Credentials, file_path: Path, filename: str) -> Optional[str]:
        """
        Upload file to Google Drive
        Returns file ID if successful, None otherwise
        """
        try:
            service = build('drive', 'v3', credentials=credentials)
            
            file_metadata = {
                'name': filename,
            }
            
            if self.folder_id:
                file_metadata['parents'] = [self.folder_id]
            
            media = MediaFileUpload(
                str(file_path),
                mimetype='application/pdf',
                resumable=True
            )
            
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()
            
            return file.get('id')
            
        except HttpError as error:
            print(f"Drive upload error: {error}")
            return None
    
    def upload_processed_files(self, credentials: Credentials, files: List[Path], filenames: List[str]) -> List[dict]:
        """Upload multiple processed files to Drive"""
        results = []
        
        for file_path, filename in zip(files, filenames):
            file_id = self.upload_file(credentials, file_path, filename)
            if file_id:
                results.append({
                    'filename': filename,
                    'file_id': file_id,
                    'success': True
                })
            else:
                results.append({
                    'filename': filename,
                    'file_id': None,
                    'success': False
                })
        
        return results
    
    def refresh_credentials(self, credentials: Credentials) -> Credentials:
        """Refresh expired credentials"""
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        return credentials

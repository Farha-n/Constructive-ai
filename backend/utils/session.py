from typing import Optional, Dict
from datetime import datetime, timedelta
import secrets
import logging

logger = logging.getLogger(__name__)

class SessionManager:
    """In-memory session manager. In production, use Redis or database."""
    
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
        self.session_expiry = timedelta(hours=24)
    
    def create_session(self, user_data: dict) -> str:
        """Create a new session and return session token."""
        session_token = secrets.token_urlsafe(32)
        self.sessions[session_token] = {
            "user_data": user_data,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + self.session_expiry
        }
        logger.info(f"Session created for user: {user_data.get('email', 'unknown')}")
        return session_token
    
    def get_session(self, session_token: str) -> Optional[Dict]:
        """Get session data if valid."""
        session = self.sessions.get(session_token)
        if not session:
            return None
        
        if datetime.now() > session["expires_at"]:
            logger.info(f"Session expired: {session_token[:10]}...")
            del self.sessions[session_token]
            return None
        
        return session
    
    def delete_session(self, session_token: str):
        """Delete a session."""
        if session_token in self.sessions:
            del self.sessions[session_token]
            logger.info(f"Session deleted: {session_token[:10]}...")
    
    def refresh_session(self, session_token: str) -> bool:
        """Refresh session expiry."""
        session = self.sessions.get(session_token)
        if session:
            session["expires_at"] = datetime.now() + self.session_expiry
            return True
        return False

# Global session manager instance
session_manager = SessionManager()


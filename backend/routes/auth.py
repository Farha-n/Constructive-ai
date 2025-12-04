from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse, JSONResponse
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
import os
import logging
from typing import Optional

from utils.session import session_manager

logger = logging.getLogger(__name__)

router = APIRouter()

# Google OAuth configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8000/auth/callback")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://mail.google.com/'
]

def get_flow():
    """Create OAuth flow instance."""
    return Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI]
            }
        },
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

@router.get("/login")
async def login():
    """Initiate Google OAuth login."""
    try:
        if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
            raise HTTPException(
                status_code=500,
                detail="OAuth credentials not configured"
            )
        
        flow = get_flow()
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        logger.info(f"OAuth login initiated")
        return {"authorization_url": authorization_url, "state": state}
    except Exception as e:
        logger.error(f"Error initiating login: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/callback")
async def callback(code: str, state: Optional[str] = None):
    """Handle OAuth callback and create session."""
    try:
        flow = get_flow()
        flow.fetch_token(code=code)
        
        credentials = flow.credentials
        
        # Get user info
        from googleapiclient.discovery import build
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        
        # Create session
        user_data = {
            "email": user_info.get("email"),
            "name": user_info.get("name"),
            "picture": user_info.get("picture"),
            "credentials": {
                "token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_uri": getattr(credentials, "token_uri", None),
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "scopes": credentials.scopes
            }
        }
        
        session_token = session_manager.create_session(user_data)
        
        logger.info(f"User authenticated: {user_info.get('email')}")
        
        # Redirect to frontend login with session token; Next.js login page will store it
        redirect_url = f"{FRONTEND_URL}/login?token={session_token}"
        return RedirectResponse(url=redirect_url)
    except Exception as e:
        logger.error(f"Error in OAuth callback: {e}")
        error_url = f"{FRONTEND_URL}/login?error=auth_failed"
        return RedirectResponse(url=error_url)

@router.get("/me")
async def get_current_user(token: str):
    """Get current user from session."""
    session = session_manager.get_session(token)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    user_data = session["user_data"]
    return {
        "email": user_data.get("email"),
        "name": user_data.get("name"),
        "picture": user_data.get("picture")
    }

@router.post("/logout")
async def logout(token: str):
    """Logout and invalidate session."""
    session_manager.delete_session(token)
    logger.info("User logged out")
    return {"message": "Logged out successfully"}

def get_credentials(token: str) -> Credentials:
    """Get Google credentials from session."""
    session = session_manager.get_session(token)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    creds_data = session["user_data"].get("credentials")
    if not creds_data:
        raise HTTPException(status_code=401, detail="No credentials found")
    
    credentials = Credentials(
        token=creds_data.get("token"),
        refresh_token=creds_data.get("refresh_token"),
        token_uri=creds_data.get("token_uri"),
        client_id=creds_data.get("client_id"),
        client_secret=creds_data.get("client_secret"),
        scopes=creds_data.get("scopes")
    )
    
    # Refresh if expired
    if not credentials.valid:
        if credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(GoogleRequest())
                # Update session with new token
                session["user_data"]["credentials"]["token"] = credentials.token
                logger.info("Credentials refreshed")
            except Exception as e:
                logger.error(f"Error refreshing credentials: {e}")
                raise HTTPException(status_code=401, detail="Failed to refresh credentials")
        else:
            raise HTTPException(status_code=401, detail="Credentials expired")
    
    return credentials


from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging

from googleapiclient.errors import HttpError

from routes.auth import get_credentials
from utils.gmail import GmailService
from utils.ai import AIService

logger = logging.getLogger(__name__)

router = APIRouter()

# Lazy initialization - only create when needed
_ai_service = None

def get_ai_service():
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service

class SendEmailRequest(BaseModel):
    to: str
    subject: str
    body: str
    thread_id: Optional[str] = None

class DeleteEmailRequest(BaseModel):
    message_id: str

@router.get("/recent")
async def get_recent_emails(token: str, max_results: int = 5):
    """Get the last N emails with AI summaries."""
    try:
        credentials = get_credentials(token)
        gmail_service = GmailService(credentials)
        
        logger.info(f"Fetching {max_results} recent emails")
        emails = gmail_service.get_recent_emails(max_results=max_results)
        
        # Generate AI summaries for each email
        emails_with_summaries = []
        for email in emails:
            try:
                summary = get_ai_service().generate_summary(
                    email['body'],
                    email['subject'],
                    email['sender_name']
                )
                email['ai_summary'] = summary
            except Exception as e:
                logger.error(f"Error generating summary: {e}")
                email['ai_summary'] = "Unable to generate summary."
            
            emails_with_summaries.append(email)
        
        logger.info(f"Successfully fetched {len(emails_with_summaries)} emails")
        return {"emails": emails_with_summaries}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching emails: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send")
async def send_email(request: SendEmailRequest, token: str):
    """Send an email via Gmail."""
    try:
        credentials = get_credentials(token)
        gmail_service = GmailService(credentials)
        
        logger.info(f"Sending email to {request.to}")
        result = gmail_service.send_email(
            to=request.to,
            subject=request.subject,
            body=request.body,
            thread_id=request.thread_id
        )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delete")
async def delete_email(request: DeleteEmailRequest, token: str):
    """Delete an email by message ID."""
    try:
        credentials = get_credentials(token)
        gmail_service = GmailService(credentials)
        
        logger.info(f"Deleting email: {request.message_id}")
        success = gmail_service.delete_email(request.message_id)
        
        return {"success": success, "message": "Email deleted successfully" if success else "Failed to delete email"}
    except HTTPException:
        raise
    except HttpError as e:
        logger.error(f"Gmail API returned error while deleting email: {e}")
        if e.resp.status == 403:
            raise HTTPException(
                status_code=403,
                detail=(
                    "Google rejected the request because the Gmail API scopes were not granted. "
                    "Make sure the Gmail API is enabled in your Google Cloud project, then remove the "
                    "app from https://myaccount.google.com/permissions and sign in again so the app "
                    "can request full Gmail access (including the https://mail.google.com/ scope)."
                )
            )
        raise HTTPException(status_code=e.resp.status, detail=e._get_reason())
    except Exception as e:
        logger.error(f"Error deleting email: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-reply")
async def generate_reply(email_id: str, token: str, user_context: Optional[str] = None):
    """Generate an AI reply for a specific email."""
    try:
        credentials = get_credentials(token)
        gmail_service = GmailService(credentials)
        
        # Fetch the email
        emails = gmail_service.get_recent_emails(max_results=50)
        target_email = None
        for email in emails:
            if email['id'] == email_id:
                target_email = email
                break
        
        if not target_email:
            raise HTTPException(status_code=404, detail="Email not found")
        
        logger.info(f"Generating reply for email: {email_id}")
        reply = get_ai_service().generate_reply(target_email, user_context)
        
        return {
            "reply": reply,
            "original_email": {
                "id": target_email['id'],
                "sender_email": target_email['sender_email'],
                "subject": target_email['subject'],
                "thread_id": target_email.get('thread_id')
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating reply: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/find-by-sender")
async def find_email_by_sender(sender_email: str, token: str):
    """Find the latest email from a specific sender."""
    try:
        credentials = get_credentials(token)
        gmail_service = GmailService(credentials)
        
        logger.info(f"Finding email from sender: {sender_email}")
        email = gmail_service.find_email_by_sender(sender_email)
        
        if not email:
            raise HTTPException(status_code=404, detail="No email found from this sender")
        
        # Generate summary
        try:
            summary = get_ai_service().generate_summary(
                email['body'],
                email['subject'],
                email['sender_name']
            )
            email['ai_summary'] = summary
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            email['ai_summary'] = "Unable to generate summary."
        
        return {"email": email}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding email: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/find-by-subject")
async def find_email_by_subject(subject_keyword: str, token: str):
    """Find the latest email containing a keyword in subject."""
    try:
        credentials = get_credentials(token)
        gmail_service = GmailService(credentials)
        
        logger.info(f"Finding email with subject keyword: {subject_keyword}")
        email = gmail_service.find_email_by_subject(subject_keyword)
        
        if not email:
            raise HTTPException(status_code=404, detail="No email found with this subject keyword")
        
        # Generate summary
        try:
            summary = get_ai_service().generate_summary(
                email['body'],
                email['subject'],
                email['sender_name']
            )
            email['ai_summary'] = summary
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            email['ai_summary'] = "Unable to generate summary."
        
        return {"email": email}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding email: {e}")
        raise HTTPException(status_code=500, detail=str(e))


from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging
import re

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


def _has_keyword(user_message: str, keywords: List[str]) -> bool:
    """Check for whole-word keyword matches to avoid false positives inside emails."""
    for keyword in keywords:
        if re.search(rf"\b{re.escape(keyword)}\b", user_message):
            return True
    return False

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    email_context: Optional[List[Dict]] = None

@router.post("/message")
async def process_chat_message(request: ChatRequest, token: str):
    """Process a chat message and return AI response with actions."""
    try:
        credentials = get_credentials(token)
        gmail_service = GmailService(credentials)
        
        user_message = request.message.lower().strip()
        email_context = request.email_context or []
        
        # Process natural language command
        command_result = get_ai_service().process_natural_language_command(
            request.message,
            email_context
        )
        
        intent = command_result.get("intent", "unknown")
        parameters = command_result.get("parameters", {})
        confidence = command_result.get("confidence", "low")
        
        response_data = {
            "intent": intent,
            "confidence": confidence,
            "message": "",
            "action": None,
            "data": None
        }
        
        # Handle different intents
        if intent == "read" or _has_keyword(user_message, ["read", "show", "fetch"]):
            # Fetch recent emails
            max_results = 5
            if "few" in user_message or "some" in user_message:
                max_results = 5
            elif "many" in user_message or "all" in user_message or "20" in user_message:
                max_results = 20
            
            emails = gmail_service.get_recent_emails(max_results=max_results)
            
            # Generate summaries
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
            
            response_data["message"] = f"I found {len(emails)} recent emails. Here they are:"
            response_data["action"] = "display_emails"
            response_data["data"] = {"emails": emails}
        
        elif intent == "reply" or _has_keyword(user_message, ["reply", "respond"]):
            # Extract email to reply to
            sender_email = parameters.get("sender_email", "")
            email_index = parameters.get("email_index", "")
            user_context = parameters.get("action_details", "")
            
            target_email = None
            
            # Try to find email from context
            if email_context:
                if email_index and email_index.isdigit():
                    idx = int(email_index) - 1
                    if 0 <= idx < len(email_context):
                        target_email = email_context[idx]
                elif sender_email:
                    for email in email_context:
                        if sender_email.lower() in email.get('sender_email', '').lower():
                            target_email = email
                            break
            
            # If not found in context, try to find by sender
            if not target_email and sender_email:
                target_email = gmail_service.find_email_by_sender(sender_email)
            
            if target_email:
                reply = get_ai_service().generate_reply(target_email, user_context)
                response_data["message"] = f"Here's a suggested reply to the email from {target_email.get('sender_name', 'the sender')}:"
                response_data["action"] = "display_reply"
                response_data["data"] = {
                    "reply": reply,
                    "original_email": {
                        "id": target_email['id'],
                        "sender_email": target_email['sender_email'],
                        "sender_name": target_email['sender_name'],
                        "subject": target_email['subject'],
                        "thread_id": target_email.get('thread_id')
                    }
                }
            else:
                response_data["message"] = "I couldn't find the email you want to reply to. Please try fetching your recent emails first or be more specific about which email to reply to."
                response_data["action"] = "error"
        
        elif intent == "delete" or _has_keyword(user_message, ["delete", "remove"]):
            # Extract email to delete
            sender_email = parameters.get("sender_email", "")
            subject_keyword = parameters.get("subject_keyword", "")
            email_index = parameters.get("email_index", "")
            
            target_email = None
            
            # Try to find email from context
            if email_context:
                if email_index and email_index.isdigit():
                    idx = int(email_index) - 1
                    if 0 <= idx < len(email_context):
                        target_email = email_context[idx]
                elif sender_email:
                    for email in email_context:
                        if sender_email.lower() in email.get('sender_email', '').lower():
                            target_email = email
                            break
                elif subject_keyword:
                    for email in email_context:
                        if subject_keyword.lower() in email.get('subject', '').lower():
                            target_email = email
                            break
            
            # If not found in context, try to find by sender or subject
            if not target_email:
                if sender_email:
                    target_email = gmail_service.find_email_by_sender(sender_email)
                elif subject_keyword:
                    target_email = gmail_service.find_email_by_subject(subject_keyword)
            
            if target_email:
                response_data["message"] = f"I found the email from {target_email.get('sender_name', 'the sender')} with subject '{target_email.get('subject', '')}'. Are you sure you want to delete it?"
                response_data["action"] = "confirm_delete"
                response_data["data"] = {
                    "email": {
                        "id": target_email['id'],
                        "sender_name": target_email['sender_name'],
                        "sender_email": target_email['sender_email'],
                        "subject": target_email['subject']
                    }
                }
            else:
                response_data["message"] = "I couldn't find the email you want to delete. Please try fetching your recent emails first or be more specific."
                response_data["action"] = "error"
        
        elif intent == "digest" or _has_keyword(user_message, ["digest", "summary"]):
            # Generate daily digest
            emails = gmail_service.get_recent_emails(max_results=20)
            digest = get_ai_service().generate_daily_digest(emails)
            
            response_data["message"] = "Here's your daily email digest:"
            response_data["action"] = "display_digest"
            response_data["data"] = {"digest": digest, "email_count": len(emails)}
        
        else:
            # Default response for unclear commands
            response_data["message"] = """I'm your AI email assistant! I can help you with:
            
• **Read emails**: "Show me my recent emails" or "Fetch last 5 emails"
• **Generate replies**: "Reply to John" or "Generate a reply to the latest email from [sender]"
• **Delete emails**: "Delete the latest email from [sender]" or "Delete email number 2"

Try asking me to fetch your emails first, and then I can help you reply or delete specific ones!"""
            response_data["action"] = "info"
        
        logger.info(f"Processed chat message: {request.message} -> {intent}")
        return response_data
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/greeting")
async def get_greeting(token: str):
    """Get greeting message with user info."""
    try:
        from routes.auth import session_manager
        session = session_manager.get_session(token)
        if not session:
            raise HTTPException(status_code=401, detail="Invalid session")
        
        user_data = session["user_data"]
        name = user_data.get("name", "there")
        
        greeting = f"""Hello {name}! 👋

I'm your AI email assistant. I can help you:
• Read and summarize your recent emails
• Generate smart, context-aware replies
• Delete specific emails based on your instructions

Just tell me what you'd like to do in natural language. For example:
- "Show me my last 5 emails"
- "Reply to the latest email from John"
- "Delete the email about invoices"

How can I help you today?"""
        
        return {
            "greeting": greeting,
            "user": {
                "name": name,
                "email": user_data.get("email")
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting greeting: {e}")
        raise HTTPException(status_code=500, detail=str(e))


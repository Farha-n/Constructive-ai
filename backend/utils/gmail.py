from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Dict, Optional
import logging
import base64
from email.utils import parseaddr
import re

logger = logging.getLogger(__name__)

class GmailService:
    """Wrapper for Gmail API operations."""
    
    def __init__(self, credentials: Credentials):
        self.credentials = credentials
        self.service = build('gmail', 'v1', credentials=credentials)
    
    def get_profile(self) -> Dict:
        """Get user's Gmail profile."""
        try:
            profile = self.service.users().getProfile(userId='me').execute()
            return {
                "email": profile.get("emailAddress"),
                "messages_total": profile.get("messagesTotal", 0),
                "threads_total": profile.get("threadsTotal", 0)
            }
        except HttpError as error:
            logger.error(f"Error getting profile: {error}")
            raise
    
    def get_recent_emails(self, max_results: int = 5) -> List[Dict]:
        """Fetch the most recent emails from inbox."""
        try:
            # Get list of messages
            results = self.service.users().messages().list(
                userId='me',
                maxResults=max_results,
                q='in:inbox'
            ).execute()
            
            messages = results.get('messages', [])
            email_list = []
            
            for msg in messages:
                try:
                    # Get full message details
                    message = self.service.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format='full'
                    ).execute()
                    
                    email_data = self._parse_message(message)
                    email_list.append(email_data)
                except HttpError as error:
                    logger.error(f"Error fetching message {msg['id']}: {error}")
                    continue
            
            return email_list
        except HttpError as error:
            logger.error(f"Error fetching emails: {error}")
            raise
    
    def _parse_message(self, message: Dict) -> Dict:
        """Parse Gmail message into structured format."""
        headers = {h['name']: h['value'] for h in message['payload'].get('headers', [])}
        
        # Extract body
        body = self._extract_body(message['payload'])
        
        # Parse sender
        from_header = headers.get('From', '')
        sender_name, sender_email = parseaddr(from_header)
        
        return {
            "id": message['id'],
            "thread_id": message.get('threadId'),
            "sender_name": sender_name or sender_email,
            "sender_email": sender_email,
            "subject": headers.get('Subject', '(No subject)'),
            "body": body,
            "date": headers.get('Date', ''),
            "snippet": message.get('snippet', ''),
            "labels": message.get('labelIds', [])
        }
    
    def _extract_body(self, payload: Dict) -> str:
        """Extract email body from payload."""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                mime_type = part.get('mimeType', '')
                if 'text/plain' in mime_type or 'text/html' in mime_type:
                    data = part.get('body', {}).get('data')
                    if data:
                        try:
                            body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                            # Strip HTML tags if it's HTML
                            if 'html' in mime_type:
                                body = re.sub(r'<[^>]+>', '', body)
                            break
                        except Exception as e:
                            logger.error(f"Error decoding body: {e}")
        else:
            # Single part message
            data = payload.get('body', {}).get('data')
            if data:
                try:
                    body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                except Exception as e:
                    logger.error(f"Error decoding body: {e}")
        
        return body.strip()
    
    def send_email(self, to: str, subject: str, body: str, thread_id: Optional[str] = None) -> Dict:
        """Send an email via Gmail."""
        try:
            from_email = self.get_profile()['email']
            
            # Create message
            message = self._create_message(from_email, to, subject, body, thread_id)
            
            # Send message
            sent_message = self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()
            
            logger.info(f"Email sent successfully: {sent_message['id']}")
            return {
                "success": True,
                "message_id": sent_message['id'],
                "thread_id": sent_message.get('threadId')
            }
        except HttpError as error:
            logger.error(f"Error sending email: {error}")
            raise
    
    def _create_message(self, sender: str, to: str, subject: str, body: str, thread_id: Optional[str] = None) -> Dict:
        """Create a Gmail message object."""
        message_text = f"From: {sender}\nTo: {to}\nSubject: {subject}\n\n{body}"
        
        message = {
            'raw': base64.urlsafe_b64encode(message_text.encode('utf-8')).decode('utf-8')
        }
        
        if thread_id:
            message['threadId'] = thread_id
        
        return message
    
    def delete_email(self, message_id: str) -> bool:
        """Delete an email by message ID."""
        try:
            self.service.users().messages().delete(
                userId='me',
                id=message_id
            ).execute()
            logger.info(f"Email deleted successfully: {message_id}")
            return True
        except HttpError as error:
            logger.error(f"Error deleting email: {error}")
            raise
    
    def find_email_by_sender(self, sender_email: str, limit: int = 1) -> Optional[Dict]:
        """Find the latest email from a specific sender."""
        try:
            results = self.service.users().messages().list(
                userId='me',
                maxResults=limit,
                q=f'from:{sender_email} in:inbox'
            ).execute()
            
            messages = results.get('messages', [])
            if not messages:
                return None
            
            message = self.service.users().messages().get(
                userId='me',
                id=messages[0]['id'],
                format='full'
            ).execute()
            
            return self._parse_message(message)
        except HttpError as error:
            logger.error(f"Error finding email by sender: {error}")
            return None
    
    def find_email_by_subject(self, subject_keyword: str, limit: int = 1) -> Optional[Dict]:
        """Find the latest email containing a keyword in subject."""
        try:
            results = self.service.users().messages().list(
                userId='me',
                maxResults=limit,
                q=f'subject:"{subject_keyword}" in:inbox'
            ).execute()
            
            messages = results.get('messages', [])
            if not messages:
                return None
            
            message = self.service.users().messages().get(
                userId='me',
                id=messages[0]['id'],
                format='full'
            ).execute()
            
            return self._parse_message(message)
        except HttpError as error:
            logger.error(f"Error finding email by subject: {error}")
            return None


from openai import OpenAI
from typing import List, Dict, Optional
import os
import logging

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI-powered email operations."""
    
    def __init__(self):
        # Check for Groq API key first, then fall back to OpenAI
        api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY or OPENAI_API_KEY environment variable is required")
        
        # If using Groq, set the base URL
        if os.getenv("GROQ_API_KEY"):
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            self.model = "llama-3.1-8b-instant"  # or another active Groq model  # Groq model
            logger.info("Using Groq API")
        else:
            self.client = OpenAI(api_key=api_key)
            self.model = "gpt-4o-mini"  # OpenAI model
            logger.info("Using OpenAI API")
    
    def generate_summary(self, email_body: str, subject: str, sender: str) -> str:
        """Generate a concise AI summary of an email."""
        try:
            prompt = f"""Please provide a brief, clear summary (2-3 sentences) of this email:

From: {sender}
Subject: {subject}

Body:
{email_body[:2000]}

Summary:"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes emails concisely."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            content = response.choices[0].message.content or ""
            summary = content.strip()
            logger.info(f"Generated summary for email from {sender}")
            return summary
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return "Unable to generate summary at this time."
    
    def generate_reply(self, original_email: Dict, user_context: str = "") -> str:
        """Generate a context-aware reply to an email."""
        try:
            sender = original_email.get('sender_name', original_email.get('sender_email', 'Unknown'))
            subject = original_email.get('subject', '')
            body = original_email.get('body', '')[:2000]
            
            prompt = f"""Write a professional, clear, and contextually appropriate email reply to this message:

From: {sender}
Subject: {subject}

Original Message:
{body}

{f'Additional context: {user_context}' if user_context else ''}

Please write a concise, professional reply that:
- Addresses the key points in the original email
- Is ready to send (no placeholders or explanations)
- Maintains a professional tone
- Is appropriate for the context

Reply:"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional email assistant that writes clear, contextually appropriate replies."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            content = response.choices[0].message.content or ""
            reply = content.strip()
            logger.info(f"Generated reply for email from {sender}")
            return reply
        except Exception as e:
            logger.error(f"Error generating reply: {e}")
            return "I apologize, but I'm having trouble generating a reply right now. Please try again later."
    
    def process_natural_language_command(self, command: str, email_context: Optional[List[Dict]] = None) -> Dict:
        """Process natural language commands and extract intent."""
        try:
            context_str = ""
            if email_context:
                context_str = "\n".join([
                    f"- From {email.get('sender_email', 'unknown')}: {email.get('subject', '')}"
                    for email in email_context[:5]
                ])
            
            prompt = f"""Analyze this user command and determine the intent:

User command: "{command}"

{f'Available emails:\n{context_str}' if email_context else 'No email context available.'}

Determine the intent and extract key parameters. Respond in this JSON format:
{{
    "intent": "read|reply|delete|digest",
    "parameters": {{
        "sender_email": "extracted sender if mentioned",
        "subject_keyword": "extracted keyword if mentioned",
        "email_index": "1-5 if referencing by number",
        "action_details": "any additional details"
    }},
    "confidence": "high|medium|low"
}}"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a command parser that extracts structured intent from natural language."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2
            )
            
            import json
            content = response.choices[0].message.content
            if content is None:
                raise ValueError("No content returned from AI when processing command")
            result = json.loads(content)
            logger.info(f"Processed command: {command} -> {result.get('intent')}")
            return result
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            return {
                "intent": "unknown",
                "parameters": {},
                "confidence": "low",
                "error": str(e)
            }
    
    def generate_daily_digest(self, emails: List[Dict]) -> str:
        """Generate a daily digest of emails."""
        try:
            emails_summary = "\n\n".join([
                f"From: {email.get('sender_email', 'unknown')}\n"
                f"Subject: {email.get('subject', '')}\n"
                f"Preview: {email.get('snippet', '')}"
                for email in emails
            ])
            
            prompt = f"""Create a concise daily email digest summarizing these emails:

{emails_summary}

Please provide:
1. Key highlights (most important emails)
2. Suggested actions or follow-ups
3. Brief categorization if helpful

Keep it concise and actionable:"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an email assistant that creates helpful daily digests."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.5
            )
            
            content = response.choices[0].message.content or ""
            digest = content.strip()
            logger.info("Generated daily digest")
            return digest
        except Exception as e:
            logger.error(f"Error generating digest: {e}")
            return "Unable to generate digest at this time."

    def generate_grouped_summary(self, emails: List[Dict]) -> str:
        """Group emails into categories (Work, Promotions, Personal, Urgent) and summarize each group."""
        try:
            emails_summary = "\n\n".join([
                f"ID: {email.get('id', '')}\n"
                f"From: {email.get('sender_email', 'unknown')}\n"
                f"Subject: {email.get('subject', '')}\n"
                f"Preview: {email.get('snippet', '')}"
                for email in emails
            ])

            prompt = f"""You are helping a user triage their inbox.

Here are some recent emails:

{emails_summary}

1. Group these emails into the following categories based on sender, subject, and preview:
   - Work
   - Promotions
   - Personal
   - Urgent
2. For each category, provide:
   - A short title line with the category name and number of emails
   - 2–4 bullet points summarizing the most important emails (reference subjects, not IDs)
3. If a category has no emails, omit it entirely.
4. Answer in clear markdown.
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an email assistant that categorizes and summarizes emails."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.4
            )

            content = response.choices[0].message.content or ""
            summary = content.strip()
            logger.info("Generated grouped summary")
            return summary
        except Exception as e:
            logger.error(f"Error generating grouped summary: {e}")
            return "Unable to generate grouped summary at this time."


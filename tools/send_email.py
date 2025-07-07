"""
Email Sending Module
This module handles sending emails via Gmail API or other email providers.
"""

import os
import json
import base64
import time
import logging
from typing import Dict, List, Any, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def save_email_locally(recipient_email: str, subject: str, body: str) -> Dict[str, Any]:
    """Save an email locally as a file.
    
    Args:
        recipient_email: Recipient's email address
        subject: Email subject line
        body: Email body content
        
    Returns:
        Dictionary with status and message
    """
    try:
        # Create directory if it doesn't exist
        email_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "emails")
        os.makedirs(email_dir, exist_ok=True)
        
        # Create filename based on timestamp and recipient
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        recipient_part = recipient_email.replace("@", "_at_").replace(".", "_")
        filename = os.path.join(email_dir, f"{timestamp}_{recipient_part}.json")
        
        # Save email data
        email_data = {
            "to": recipient_email,
            "subject": subject,
            "body": body,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(email_data, f, indent=2)
        
        logger.info(f"Email saved locally to {filename}")
        
        return {
            "status": "success",
            "message": f"Email saved locally to {filename}",
            "provider": "local_file",
            "file_path": filename
        }
    except Exception as e:
        logger.error(f"Failed to save email locally: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to save email locally: {str(e)}"
        }

def send_email_via_gmail(recipient_email: str, subject: str, body: str) -> Dict[str, Any]:
    """Send an email using Gmail API.
    
    Args:
        recipient_email: Recipient's email address
        subject: Email subject line
        body: Email body content
        
    Returns:
        Dictionary with status and message
    """
    try:
        # Check if we're in test mode
        if os.getenv("TEST_MODE", "false").lower() == "true":
            # In test mode, just log the email instead of sending
            logger.info(f"TEST MODE: Would send email via Gmail to {recipient_email}")
            
            # Save email locally in test mode
            return save_email_locally(recipient_email, subject, body)
        
        # For actual sending, we need the Gmail API
        try:
            from googleapiclient.discovery import build
            from google.oauth2.credentials import Credentials
        except ImportError:
            logger.error("Gmail API libraries not installed")
            return {
                "status": "error",
                "message": "Gmail API libraries not installed. Run: pip install google-api-python-client google-auth google-auth-oauthlib"
            }
        
        # Load Gmail credentials
        creds_file = os.getenv("GMAIL_CREDENTIALS")
        if not creds_file or not os.path.exists(creds_file):
            logger.error("Gmail credentials file not found")
            return {
                "status": "error",
                "message": "Gmail credentials file not found. Set GMAIL_CREDENTIALS env var to point to your credentials.json file."
            }
        
        # Load credentials and build service
        creds = Credentials.from_authorized_user_info(json.load(open(creds_file)))
        service = build('gmail', 'v1', credentials=creds)
        
        # Create message
        message = MIMEMultipart()
        message['to'] = recipient_email
        message['subject'] = subject
        message.attach(MIMEText(body, 'plain'))
        
        # Encode message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        # Send message
        send_message = service.users().messages().send(
            userId="me", 
            body={'raw': encoded_message}
        ).execute()
        
        logger.info(f"Email sent via Gmail API to {recipient_email}")
        
        # Also save locally as backup
        save_email_locally(recipient_email, subject, body)
        
        return {
            "status": "success",
            "message": f"Email sent via Gmail API",
            "message_id": send_message.get('id'),
            "provider": "gmail"
        }
    except Exception as e:
        logger.error(f"Failed to send email via Gmail: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to send email via Gmail: {str(e)}"
        }

def send_email_via_mailersend(recipient_email: str, subject: str, body: str) -> Dict[str, Any]:
    """Send an email using MailerSend API.
    
    Args:
        recipient_email: Recipient's email address
        subject: Email subject line
        body: Email body content
        
    Returns:
        Dictionary with status and message
    """
    try:
        # Check if we're in test mode
        if os.getenv("TEST_MODE", "false").lower() == "true":
            logger.info(f"TEST MODE: Would send email via MailerSend to {recipient_email}")
            
            # Save email locally in test mode
            return save_email_locally(recipient_email, subject, body)
        
        try:
            import requests
        except ImportError:
            logger.error("Requests library not installed")
            return {
                "status": "error",
                "message": "Requests library not installed. Run: pip install requests"
            }
        
        api_key = os.getenv("MAILERSEND_API_KEY")
        if not api_key:
            logger.error("MailerSend API key not found")
            return {
                "status": "error",
                "message": "MailerSend API key not found in environment variables"
            }
        
        from_email = os.getenv("MAILERSEND_FROM_EMAIL")
        from_name = os.getenv("MAILERSEND_FROM_NAME", "AI SDR Agent")
        
        if not from_email:
            logger.error("MailerSend from email not found")
            return {
                "status": "error",
                "message": "MailerSend from email not found in environment variables"
            }
        
        url = "https://api.mailersend.com/v1/email"
        headers = {
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "from": {
                "email": from_email,
                "name": from_name
            },
            "to": [
                {
                    "email": recipient_email
                }
            ],
            "subject": subject,
            "text": body
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 202:
            logger.info(f"Email sent via MailerSend API to {recipient_email}")
            
            # Also save locally as backup
            save_email_locally(recipient_email, subject, body)
            
            return {
                "status": "success",
                "message": "Email sent via MailerSend API",
                "provider": "mailersend"
            }
        else:
            logger.error(f"MailerSend API error: {response.text}")
            return {
                "status": "error",
                "message": f"MailerSend API error: {response.text}"
            }
    except Exception as e:
        logger.error(f"Failed to send email via MailerSend: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to send email via MailerSend: {str(e)}"
        }

def send_email_via_sendgrid(recipient_email: str, subject: str, body: str) -> Dict[str, Any]:
    """Send an email using SendGrid API.
    
    Args:
        recipient_email: Recipient's email address
        subject: Email subject line
        body: Email body content
        
    Returns:
        Dictionary with status and message
    """
    try:
        # Check if we're in test mode
        if os.getenv("TEST_MODE", "false").lower() == "true":
            logger.info(f"TEST MODE: Would send email via SendGrid to {recipient_email}")
            
            # Save email locally in test mode
            return save_email_locally(recipient_email, subject, body)
        
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail
        except ImportError:
            logger.error("SendGrid library not installed")
            return {
                "status": "error",
                "message": "SendGrid library not installed. Run: pip install sendgrid"
            }
        
        api_key = os.getenv("SENDGRID_API_KEY")
        if not api_key:
            logger.error("SendGrid API key not found")
            return {
                "status": "error",
                "message": "SendGrid API key not found in environment variables"
            }
        
        from_email = os.getenv("SENDGRID_FROM_EMAIL")
        if not from_email:
            logger.error("SendGrid from email not found")
            return {
                "status": "error",
                "message": "SendGrid from email not found in environment variables"
            }
        
        message = Mail(
            from_email=from_email,
            to_emails=recipient_email,
            subject=subject,
            plain_text_content=body
        )
        
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        
        if response.status_code in [200, 201, 202]:
            logger.info(f"Email sent via SendGrid API to {recipient_email}")
            
            # Also save locally as backup
            save_email_locally(recipient_email, subject, body)
            
            return {
                "status": "success",
                "message": "Email sent via SendGrid API",
                "provider": "sendgrid"
            }
        else:
            logger.error(f"SendGrid API error: {response.body}")
            return {
                "status": "error",
                "message": f"SendGrid API error: {response.body}"
            }
    except Exception as e:
        logger.error(f"Failed to send email via SendGrid: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to send email via SendGrid: {str(e)}"
        }

def send_email_via_lemlist(recipient_email: str, subject: str, body: str) -> Dict[str, Any]:
    """Send an email using Lemlist API.
    
    Args:
        recipient_email: Recipient's email address
        subject: Email subject line
        body: Email body content
        
    Returns:
        Dictionary with status and message
    """
    try:
        # Check if we're in test mode
        if os.getenv("TEST_MODE", "false").lower() == "true":
            logger.info(f"TEST MODE: Would send email via Lemlist to {recipient_email}")
            
            # Save email locally in test mode
            return save_email_locally(recipient_email, subject, body)
        
        try:
            import requests
        except ImportError:
            logger.error("Requests library not installed")
            return {
                "status": "error",
                "message": "Requests library not installed. Run: pip install requests"
            }
        
        api_key = os.getenv("LEMLIST_API_KEY")
        if not api_key:
            logger.error("Lemlist API key not found")
            return {
                "status": "error",
                "message": "Lemlist API key not found in environment variables"
            }
        
        # Get campaign ID (required by Lemlist)
        campaign_id = os.getenv("LEMLIST_CAMPAIGN_ID")
        if not campaign_id:
            logger.error("Lemlist campaign ID not found")
            return {
                "status": "error",
                "message": "Lemlist campaign ID not found in environment variables"
            }
        
        # Lemlist API endpoint
        url = f"https://api.lemlist.com/api/campaigns/{campaign_id}/leads"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # Lemlist requires adding a lead to a campaign
        payload = {
            "email": recipient_email,
            "firstName": recipient_email.split("@")[0],  # Use part before @ as first name
            "customFields": {
                "subject": subject,
                "message": body
            }
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code in [200, 201]:
            logger.info(f"Lead added to Lemlist campaign for {recipient_email}")
            
            # Also save locally as backup
            save_email_locally(recipient_email, subject, body)
            
            return {
                "status": "success",
                "message": "Lead added to Lemlist campaign",
                "provider": "lemlist"
            }
        else:
            logger.error(f"Lemlist API error: {response.text}")
            return {
                "status": "error",
                "message": f"Lemlist API error: {response.text}"
            }
    except Exception as e:
        logger.error(f"Failed to send via Lemlist: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to send via Lemlist: {str(e)}"
        }

def send_email(recipient_email: str, subject: str, body: str) -> Dict[str, Any]:
    """Main function to send an email using the configured provider with fallbacks.
    
    Args:
        recipient_email: Recipient's email address
        subject: Email subject line
        body: Email body content
        
    Returns:
        Dictionary with status and message
    """
    # Get the email provider from environment or use Gmail as default
    email_provider = os.getenv("EMAIL_PROVIDER", "gmail").lower()
    test_mode = os.getenv("TEST_MODE", "false").lower() == "true"
    
    # In test mode, always save locally
    if test_mode:
        logger.info(f"Running in test mode, saving email locally")
        return save_email_locally(recipient_email, subject, body)
    
    # Try primary provider
    if email_provider == "gmail":
        logger.info(f"Sending email via Gmail to {recipient_email}")
        result = send_email_via_gmail(recipient_email, subject, body)
        
        # If Gmail fails, try MailerSend
        if "error" in result.get("status", ""):
            logger.warning(f"Gmail failed: {result.get('message')}")
            logger.info(f"Falling back to MailerSend")
            result = send_email_via_mailersend(recipient_email, subject, body)
            
            # If MailerSend fails, try SendGrid
            if "error" in result.get("status", ""):
                logger.warning(f"MailerSend failed: {result.get('message')}")
                logger.info(f"Falling back to SendGrid")
                result = send_email_via_sendgrid(recipient_email, subject, body)
                
                # If SendGrid fails, try Lemlist
                if "error" in result.get("status", ""):
                    logger.warning(f"SendGrid failed: {result.get('message')}")
                    logger.info(f"Falling back to Lemlist")
                    result = send_email_via_lemlist(recipient_email, subject, body)
                    
                    # If all providers fail, save locally
                    if "error" in result.get("status", ""):
                        logger.warning(f"Lemlist failed: {result.get('message')}")
                        logger.info(f"Falling back to local storage")
                        result = save_email_locally(recipient_email, subject, body)
    
    elif email_provider == "mailersend":
        logger.info(f"Sending email via MailerSend to {recipient_email}")
        result = send_email_via_mailersend(recipient_email, subject, body)
        
        # If MailerSend fails, try Gmail
        if "error" in result.get("status", ""):
            logger.warning(f"MailerSend failed: {result.get('message')}")
            logger.info(f"Falling back to Gmail")
            result = send_email_via_gmail(recipient_email, subject, body)
            
            # If Gmail fails, try SendGrid
            if "error" in result.get("status", ""):
                logger.warning(f"Gmail failed: {result.get('message')}")
                logger.info(f"Falling back to SendGrid")
                result = send_email_via_sendgrid(recipient_email, subject, body)
                
                # If SendGrid fails, try Lemlist
                if "error" in result.get("status", ""):
                    logger.warning(f"SendGrid failed: {result.get('message')}")
                    logger.info(f"Falling back to Lemlist")
                    result = send_email_via_lemlist(recipient_email, subject, body)
                    
                    # If all providers fail, save locally
                    if "error" in result.get("status", ""):
                        logger.warning(f"Lemlist failed: {result.get('message')}")
                        logger.info(f"Falling back to local storage")
                        result = save_email_locally(recipient_email, subject, body)
    
    elif email_provider == "sendgrid":
        logger.info(f"Sending email via SendGrid to {recipient_email}")
        result = send_email_via_sendgrid(recipient_email, subject, body)
        
        # If SendGrid fails, try Gmail
        if "error" in result.get("status", ""):
            logger.warning(f"SendGrid failed: {result.get('message')}")
            logger.info(f"Falling back to Gmail")
            result = send_email_via_gmail(recipient_email, subject, body)
            
            # If Gmail fails, try MailerSend
            if "error" in result.get("status", ""):
                logger.warning(f"Gmail failed: {result.get('message')}")
                logger.info(f"Falling back to MailerSend")
                result = send_email_via_mailersend(recipient_email, subject, body)
                
                # If MailerSend fails, try Lemlist
                if "error" in result.get("status", ""):
                    logger.warning(f"MailerSend failed: {result.get('message')}")
                    logger.info(f"Falling back to Lemlist")
                    result = send_email_via_lemlist(recipient_email, subject, body)
                    
                    # If all providers fail, save locally
                    if "error" in result.get("status", ""):
                        logger.warning(f"Lemlist failed: {result.get('message')}")
                        logger.info(f"Falling back to local storage")
                        result = save_email_locally(recipient_email, subject, body)
    
    elif email_provider == "lemlist":
        logger.info(f"Sending email via Lemlist to {recipient_email}")
        result = send_email_via_lemlist(recipient_email, subject, body)
        
        # If Lemlist fails, try Gmail
        if "error" in result.get("status", ""):
            logger.warning(f"Lemlist failed: {result.get('message')}")
            logger.info(f"Falling back to Gmail")
            result = send_email_via_gmail(recipient_email, subject, body)
            
            # If Gmail fails, try MailerSend
            if "error" in result.get("status", ""):
                logger.warning(f"Gmail failed: {result.get('message')}")
                logger.info(f"Falling back to MailerSend")
                result = send_email_via_mailersend(recipient_email, subject, body)
                
                # If MailerSend fails, try SendGrid
                if "error" in result.get("status", ""):
                    logger.warning(f"MailerSend failed: {result.get('message')}")
                    logger.info(f"Falling back to SendGrid")
                    result = send_email_via_sendgrid(recipient_email, subject, body)
                    
                    # If all providers fail, save locally
                    if "error" in result.get("status", ""):
                        logger.warning(f"SendGrid failed: {result.get('message')}")
                        logger.info(f"Falling back to local storage")
                        result = save_email_locally(recipient_email, subject, body)
    
    else:
        logger.warning(f"Unknown email provider: {email_provider}")
        logger.info(f"Using local storage as fallback")
        result = save_email_locally(recipient_email, subject, body)
    
    return result 
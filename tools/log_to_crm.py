"""
CRM Logging Module
This module handles logging lead interactions to a CRM system.
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def log_to_airtable(name: str, email: str, company: str, status: str, notes: str = "") -> Dict[str, Any]:
    """Log lead interaction to Airtable.
    
    Args:
        name: Lead's name
        email: Lead's email address
        company: Lead's company
        status: Current status (e.g., sent, replied, bounced)
        notes: Additional notes about the interaction
        
    Returns:
        Dictionary with status and message
    """
    try:
        # Check if we're in test mode
        if os.getenv("TEST_MODE", "false").lower() == "true":
            logger.info(f"TEST MODE: Would log to Airtable - {name} ({email}) from {company}")
            
            # Save locally in test mode
            return log_to_local_csv(name, email, company, status, notes)
        
        try:
            import requests
        except ImportError:
            logger.error("Requests library not installed")
            return {
                "status": "error",
                "message": "Requests library not installed. Run: pip install requests"
            }
        
        api_key = os.getenv("AIRTABLE_API_KEY")
        base_id = os.getenv("AIRTABLE_BASE_ID")
        table_name = os.getenv("AIRTABLE_TABLE_NAME", "Leads")
        
        if not api_key:
            logger.error("Airtable API key not found")
            return {
                "status": "error",
                "message": "Airtable API key not found in environment variables"
            }
        
        if not base_id:
            logger.error("Airtable base ID not found")
            return {
                "status": "error",
                "message": "Airtable base ID not found in environment variables"
            }
        
        url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "fields": {
                "Name": name,
                "Email": email,
                "Company": company,
                "Status": status,
                "Notes": notes,
                "Last Contact": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200 or response.status_code == 201:
            logger.info(f"Lead logged to Airtable: {name} ({email}) from {company}")
            
            # Also save locally as backup
            log_to_local_csv(name, email, company, status, notes)
            
            return {
                "status": "success",
                "message": "Lead logged to Airtable",
                "record_id": response.json().get("id"),
                "provider": "airtable"
            }
        else:
            logger.error(f"Airtable API error: {response.text}")
            return {
                "status": "error",
                "message": f"Airtable API error: {response.text}"
            }
    except Exception as e:
        logger.error(f"Failed to log to Airtable: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to log to Airtable: {str(e)}"
        }

def log_to_supabase(name: str, email: str, company: str, status: str, notes: str = "") -> Dict[str, Any]:
    """Log lead interaction to Supabase.
    
    Args:
        name: Lead's name
        email: Lead's email address
        company: Lead's company
        status: Current status (e.g., sent, replied, bounced)
        notes: Additional notes about the interaction
        
    Returns:
        Dictionary with status and message
    """
    try:
        # Check if we're in test mode
        if os.getenv("TEST_MODE", "false").lower() == "true":
            logger.info(f"TEST MODE: Would log to Supabase - {name} ({email}) from {company}")
            
            # Save locally in test mode
            return log_to_local_csv(name, email, company, status, notes)
        
        try:
            from supabase import create_client, Client
        except ImportError:
            logger.error("Supabase library not installed")
            return {
                "status": "error",
                "message": "Supabase library not installed. Run: pip install supabase"
            }
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        table_name = os.getenv("SUPABASE_TABLE_NAME", "leads")
        
        if not url or not key:
            logger.error("Supabase URL or key not found")
            return {
                "status": "error",
                "message": "Supabase URL or key not found in environment variables"
            }
        
        # Initialize Supabase client
        supabase: Client = create_client(url, key)
        
        # Insert lead data
        data = {
            "name": name,
            "email": email,
            "company": company,
            "status": status,
            "notes": notes,
            "last_contact": datetime.now().isoformat()
        }
        
        response = supabase.table(table_name).insert(data).execute()
        
        if hasattr(response, "data") and response.data:
            logger.info(f"Lead logged to Supabase: {name} ({email}) from {company}")
            
            # Also save locally as backup
            log_to_local_csv(name, email, company, status, notes)
            
            return {
                "status": "success",
                "message": "Lead logged to Supabase",
                "record_id": response.data[0].get("id") if response.data else None,
                "provider": "supabase"
            }
        else:
            logger.error(f"Supabase error: {response.error if hasattr(response, 'error') else 'Unknown error'}")
            return {
                "status": "error",
                "message": f"Supabase error: {response.error if hasattr(response, 'error') else 'Unknown error'}"
            }
    except Exception as e:
        logger.error(f"Failed to log to Supabase: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to log to Supabase: {str(e)}"
        }

def log_to_notion(name: str, email: str, company: str, status: str, notes: str = "") -> Dict[str, Any]:
    """Log lead interaction to Notion.
    
    Args:
        name: Lead's name
        email: Lead's email address
        company: Lead's company
        status: Current status (e.g., sent, replied, bounced)
        notes: Additional notes about the interaction
        
    Returns:
        Dictionary with status and message
    """
    try:
        # Check if we're in test mode
        if os.getenv("TEST_MODE", "false").lower() == "true":
            logger.info(f"TEST MODE: Would log to Notion - {name} ({email}) from {company}")
            
            # Save locally in test mode
            return log_to_local_csv(name, email, company, status, notes)
        
        try:
            from notion_client import Client
        except ImportError:
            logger.error("Notion client not installed")
            return {
                "status": "error",
                "message": "Notion client not installed. Run: pip install notion-client"
            }
        
        token = os.getenv("NOTION_TOKEN")
        database_id = os.getenv("NOTION_DATABASE_ID")
        
        if not token:
            logger.error("Notion token not found")
            return {
                "status": "error",
                "message": "Notion token not found in environment variables"
            }
        
        if not database_id:
            logger.error("Notion database ID not found")
            return {
                "status": "error",
                "message": "Notion database ID not found in environment variables"
            }
        
        # Initialize Notion client
        notion = Client(auth=token)
        
        # Create page in database
        response = notion.pages.create(
            parent={"database_id": database_id},
            properties={
                "Name": {"title": [{"text": {"content": name}}]},
                "Email": {"email": email},
                "Company": {"rich_text": [{"text": {"content": company}}]},
                "Status": {"select": {"name": status}},
                "Notes": {"rich_text": [{"text": {"content": notes}}]},
                "Last Contact": {"date": {"start": datetime.now().isoformat()}}
            }
        )
        
        if response and "id" in response:
            logger.info(f"Lead logged to Notion: {name} ({email}) from {company}")
            
            # Also save locally as backup
            log_to_local_csv(name, email, company, status, notes)
            
            return {
                "status": "success",
                "message": "Lead logged to Notion",
                "page_id": response.get("id"),
                "provider": "notion"
            }
        else:
            logger.error("Failed to create Notion page")
            return {
                "status": "error",
                "message": "Failed to create Notion page"
            }
    except Exception as e:
        logger.error(f"Failed to log to Notion: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to log to Notion: {str(e)}"
        }

def log_to_google_sheets(name: str, email: str, company: str, status: str, notes: str = "") -> Dict[str, Any]:
    """Log lead interaction to Google Sheets.
    
    Args:
        name: Lead's name
        email: Lead's email address
        company: Lead's company
        status: Current status (e.g., sent, replied, bounced)
        notes: Additional notes about the interaction
        
    Returns:
        Dictionary with status and message
    """
    try:
        # Check if we're in test mode
        if os.getenv("TEST_MODE", "false").lower() == "true":
            logger.info(f"TEST MODE: Would log to Google Sheets - {name} ({email}) from {company}")
            
            # Save locally in test mode
            return log_to_local_csv(name, email, company, status, notes)
        
        try:
            from googleapiclient.discovery import build
            from google.oauth2.service_account import Credentials
        except ImportError:
            logger.error("Google API libraries not installed")
            return {
                "status": "error",
                "message": "Google API libraries not installed. Run: pip install google-api-python-client google-auth google-auth-oauthlib"
            }
        
        # Get credentials file path
        creds_file = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
        spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")
        sheet_name = os.getenv("GOOGLE_SHEETS_TAB", "Leads")
        
        if not creds_file or not os.path.exists(creds_file):
            logger.error("Google Sheets credentials file not found")
            return {
                "status": "error",
                "message": "Google Sheets credentials file not found. Set GOOGLE_SHEETS_CREDENTIALS env var."
            }
        
        if not spreadsheet_id:
            logger.error("Google Sheets ID not found")
            return {
                "status": "error",
                "message": "Google Sheets ID not found in environment variables"
            }
        
        # Load credentials and build service
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        creds = Credentials.from_service_account_file(creds_file, scopes=scopes)
        service = build('sheets', 'v4', credentials=creds)
        
        # Prepare values to append
        values = [
            [
                name,
                email,
                company,
                status,
                notes,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]
        ]
        
        # Append values to sheet
        body = {
            'values': values
        }
        
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A:F",
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        
        if result and 'updates' in result:
            logger.info(f"Lead logged to Google Sheets: {name} ({email}) from {company}")
            
            # Also save locally as backup
            log_to_local_csv(name, email, company, status, notes)
            
            return {
                "status": "success",
                "message": "Lead logged to Google Sheets",
                "updated_range": result.get('updates', {}).get('updatedRange'),
                "provider": "google_sheets"
            }
        else:
            logger.error("Failed to append to Google Sheets")
            return {
                "status": "error",
                "message": "Failed to append to Google Sheets"
            }
    except Exception as e:
        logger.error(f"Failed to log to Google Sheets: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to log to Google Sheets: {str(e)}"
        }

def log_to_local_csv(name: str, email: str, company: str, status: str, notes: str = "") -> Dict[str, Any]:
    """Log lead interaction to a local CSV file (fallback option).
    
    Args:
        name: Lead's name
        email: Lead's email address
        company: Lead's company
        status: Current status (e.g., sent, replied, bounced)
        notes: Additional notes about the interaction
        
    Returns:
        Dictionary with status and message
    """
    try:
        import csv
        from pathlib import Path
        
        # Create data directory if it doesn't exist
        data_dir = Path(os.path.dirname(os.path.dirname(__file__))) / "data"
        data_dir.mkdir(exist_ok=True)
        
        # Create or append to CSV file
        csv_path = data_dir / "leads.csv"
        file_exists = csv_path.exists()
        
        with open(csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            
            # Write header if file is new
            if not file_exists:
                writer.writerow(["Name", "Email", "Company", "Status", "Notes", "Timestamp"])
            
            # Write lead data
            writer.writerow([
                name,
                email,
                company,
                status,
                notes,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])
        
        logger.info(f"Lead logged to local CSV: {name} ({email}) from {company}")
        
        return {
            "status": "success",
            "message": f"Lead logged to local CSV file: {csv_path}",
            "provider": "local_csv"
        }
    except Exception as e:
        logger.error(f"Failed to log to local CSV: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to log to local CSV: {str(e)}"
        }

def log_to_crm(name: str, email: str, company: str, status: str, notes: str = "") -> Dict[str, Any]:
    """Main function to log lead interaction to the configured CRM with fallbacks.
    
    Args:
        name: Lead's name
        email: Lead's email address
        company: Lead's company
        status: Current status (e.g., sent, replied, bounced)
        notes: Additional notes about the interaction
        
    Returns:
        Dictionary with status and message
    """
    # Get the CRM provider from environment or use local CSV as default
    crm_provider = os.getenv("CRM_PROVIDER", "local_csv").lower()
    test_mode = os.getenv("TEST_MODE", "false").lower() == "true"
    
    # In test mode, always save locally
    if test_mode:
        logger.info(f"Running in test mode, saving lead locally")
        return log_to_local_csv(name, email, company, status, notes)
    
    # Try primary provider
    if crm_provider == "airtable":
        logger.info(f"Logging lead to Airtable: {name} ({email}) from {company}")
        result = log_to_airtable(name, email, company, status, notes)
        
        # If Airtable fails, try Supabase
        if result.get("status") == "error":
            logger.warning(f"Airtable failed: {result.get('message')}")
            logger.info(f"Falling back to Supabase")
            result = log_to_supabase(name, email, company, status, notes)
            
            # If Supabase fails, try Notion
            if result.get("status") == "error":
                logger.warning(f"Supabase failed: {result.get('message')}")
                logger.info(f"Falling back to Notion")
                result = log_to_notion(name, email, company, status, notes)
                
                # If Notion fails, try Google Sheets
                if result.get("status") == "error":
                    logger.warning(f"Notion failed: {result.get('message')}")
                    logger.info(f"Falling back to Google Sheets")
                    result = log_to_google_sheets(name, email, company, status, notes)
                    
                    # If all providers fail, save locally
                    if result.get("status") == "error":
                        logger.warning(f"Google Sheets failed: {result.get('message')}")
                        logger.info(f"Falling back to local CSV")
                        result = log_to_local_csv(name, email, company, status, notes)
    
    elif crm_provider == "supabase":
        logger.info(f"Logging lead to Supabase: {name} ({email}) from {company}")
        result = log_to_supabase(name, email, company, status, notes)
        
        # If Supabase fails, try Airtable
        if result.get("status") == "error":
            logger.warning(f"Supabase failed: {result.get('message')}")
            logger.info(f"Falling back to Airtable")
            result = log_to_airtable(name, email, company, status, notes)
            
            # If Airtable fails, try Notion
            if result.get("status") == "error":
                logger.warning(f"Airtable failed: {result.get('message')}")
                logger.info(f"Falling back to Notion")
                result = log_to_notion(name, email, company, status, notes)
                
                # If Notion fails, try Google Sheets
                if result.get("status") == "error":
                    logger.warning(f"Notion failed: {result.get('message')}")
                    logger.info(f"Falling back to Google Sheets")
                    result = log_to_google_sheets(name, email, company, status, notes)
                    
                    # If all providers fail, save locally
                    if result.get("status") == "error":
                        logger.warning(f"Google Sheets failed: {result.get('message')}")
                        logger.info(f"Falling back to local CSV")
                        result = log_to_local_csv(name, email, company, status, notes)
    
    elif crm_provider == "notion":
        logger.info(f"Logging lead to Notion: {name} ({email}) from {company}")
        result = log_to_notion(name, email, company, status, notes)
        
        # If Notion fails, try Airtable
        if result.get("status") == "error":
            logger.warning(f"Notion failed: {result.get('message')}")
            logger.info(f"Falling back to Airtable")
            result = log_to_airtable(name, email, company, status, notes)
            
            # If Airtable fails, try Supabase
            if result.get("status") == "error":
                logger.warning(f"Airtable failed: {result.get('message')}")
                logger.info(f"Falling back to Supabase")
                result = log_to_supabase(name, email, company, status, notes)
                
                # If Supabase fails, try Google Sheets
                if result.get("status") == "error":
                    logger.warning(f"Supabase failed: {result.get('message')}")
                    logger.info(f"Falling back to Google Sheets")
                    result = log_to_google_sheets(name, email, company, status, notes)
                    
                    # If all providers fail, save locally
                    if result.get("status") == "error":
                        logger.warning(f"Google Sheets failed: {result.get('message')}")
                        logger.info(f"Falling back to local CSV")
                        result = log_to_local_csv(name, email, company, status, notes)
    
    elif crm_provider == "google_sheets":
        logger.info(f"Logging lead to Google Sheets: {name} ({email}) from {company}")
        result = log_to_google_sheets(name, email, company, status, notes)
        
        # If Google Sheets fails, try Airtable
        if result.get("status") == "error":
            logger.warning(f"Google Sheets failed: {result.get('message')}")
            logger.info(f"Falling back to Airtable")
            result = log_to_airtable(name, email, company, status, notes)
            
            # If Airtable fails, try Supabase
            if result.get("status") == "error":
                logger.warning(f"Airtable failed: {result.get('message')}")
                logger.info(f"Falling back to Supabase")
                result = log_to_supabase(name, email, company, status, notes)
                
                # If Supabase fails, try Notion
                if result.get("status") == "error":
                    logger.warning(f"Supabase failed: {result.get('message')}")
                    logger.info(f"Falling back to Notion")
                    result = log_to_notion(name, email, company, status, notes)
                    
                    # If all providers fail, save locally
                    if result.get("status") == "error":
                        logger.warning(f"Notion failed: {result.get('message')}")
                        logger.info(f"Falling back to local CSV")
                        result = log_to_local_csv(name, email, company, status, notes)
    
    else:
        logger.info(f"Using local CSV to log lead: {name} ({email}) from {company}")
        result = log_to_local_csv(name, email, company, status, notes)
    
    return result 
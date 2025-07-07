"""
Email Writing Module
This module handles generating personalized cold emails for prospects.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
import openai

# Import scrape_website function
from .scrape_website import scrape_website

# Import interaction tools
try:
    from .interaction import get_user_input, remember, recall, confirm_action
except ImportError:
    # Handle the case when running directly
    import sys
    import os.path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from tools.interaction import get_user_input, remember, recall, confirm_action

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_email_template(template_name: str = "cold_email") -> str:
    """Load an email template from the prompts directory.
    
    Args:
        template_name: Name of the template file (without extension)
        
    Returns:
        Template content as string
    """
    template_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "prompts",
        f"{template_name}.txt"
    )
    
    # Create default template if it doesn't exist
    if not os.path.exists(template_path):
        os.makedirs(os.path.dirname(template_path), exist_ok=True)
        with open(template_path, "w", encoding="utf-8") as f:
            f.write("""Write a personalized cold email to {{name}}, the {{title}} of {{company}}.

Context: They run a {{industry}} company in {{location}}.

About their company: {{company_info}}

Product: {{product}}

Tone: Conversational and value-driven. Keep it concise (3-4 sentences max).

Include:
1. Personalized opening based on their role/company and website content
2. Brief value proposition 
3. One clear call-to-action (schedule a call)

Do NOT use generic phrases like "I hope this email finds you well."
Do NOT include pricing or technical details.
""")
    
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()

def write_email_with_openai(prompt: str) -> Dict[str, Any]:
    """Write a personalized cold email using OpenAI's GPT models.
    
    Args:
        prompt: The prompt for email generation
        
    Returns:
        Dictionary with email subject and body
    """
    try:
        # Initialize OpenAI client
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        model = os.getenv("OPENAI_MODEL", "gpt-4")
        
        # Call GPT to generate the email
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert SDR who writes highly effective, personalized cold emails."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        email_content = response.choices[0].message.content
        return email_content
    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to generate email with OpenAI: {str(e)}"
        }

def write_email_with_gemini(prompt: str) -> Dict[str, Any]:
    """Write a personalized cold email using Google's Gemini models.
    
    Args:
        prompt: The prompt for email generation
        
    Returns:
        Dictionary with email subject and body
    """
    try:
        # Import and configure Gemini
        try:
            import google.generativeai as genai
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        except ImportError:
            return {
                "status": "error",
                "message": "Google Generative AI package not installed. Run: pip install google-generativeai"
            }
        
        model = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")
        
        # Create Gemini model
        gemini_model = genai.GenerativeModel(
            model_name=model,
            generation_config={"temperature": 0.7}
        )
        
        # Generate email
        response = gemini_model.generate_content([
            {"role": "user", "parts": [{"text": "You are an expert SDR who writes highly effective, personalized cold emails."}]},
            {"role": "model", "parts": [{"text": "I'll help you write personalized, effective cold emails that drive results."}]},
            {"role": "user", "parts": [{"text": prompt}]}
        ])
        
        email_content = response.text if hasattr(response, "text") else ""
        return email_content
    except Exception as e:
        logger.error(f"Gemini API error: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to generate email with Gemini: {str(e)}"
        }

def get_company_info(company: str, website: str = None) -> str:
    """Get company information for personalization.
    
    Args:
        company: Company name
        website: Company website URL (optional)
        
    Returns:
        Company information as string
    """
    # If website is provided, scrape it
    if website:
        logger.info(f"Scraping website for {company}: {website}")
        result = scrape_website(website)
        
        if "error" not in result and "company_info" in result:
            company_info = result["company_info"]
            return company_info.get("description", "")
    
    # If no website or scraping failed, return generic info
    return f"{company} is a company in the industry."

def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length] + "..."

def write_email(name: str, title: str, company: str, industry: str, product_description: str, website: str = None) -> Dict[str, Any]:
    """Write a personalized cold email to a prospect using the configured LLM.
    
    Args:
        name: Recipient's name
        title: Recipient's job title
        company: Recipient's company
        industry: Recipient's industry
        product_description: Description of your product/service
        website: Company website URL (optional)
        
    Returns:
        Dictionary with email subject and body
    """
    try:
        # Load the email template
        template = load_email_template("cold_email")
        
        # Get company information for personalization
        company_info = get_company_info(company, website)
        
        # Replace template variables
        prompt = template.replace("{{name}}", name)
        prompt = prompt.replace("{{title}}", title)
        prompt = prompt.replace("{{company}}", company)
        prompt = prompt.replace("{{industry}}", industry)
        prompt = prompt.replace("{{product}}", product_description)
        prompt = prompt.replace("{{company_info}}", truncate_text(company_info))
        
        # Determine which LLM to use
        llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()
        test_mode = os.getenv("TEST_MODE", "false").lower() == "true"
        
        # In test mode, use a template email
        if test_mode:
            logger.info("Running in test mode, using template email")
            return {
                "status": "success",
                "subject": f"Quick question about {company}",
                "body": f"Hi {name},\n\nI noticed {company} is doing interesting work in the {industry} space. Our {product_description} might be a good fit for your needs.\n\nDo you have 15 minutes to chat this week?\n\nBest,\nAI SDR"
            }
        
        # Generate email with the appropriate LLM
        if llm_provider == "gemini":
            logger.info("Generating email with Gemini")
            email_content = write_email_with_gemini(prompt)
        else:
            logger.info("Generating email with OpenAI")
            email_content = write_email_with_openai(prompt)
        
        # Check if there was an error
        if isinstance(email_content, dict) and "status" in email_content and email_content["status"] == "error":
            # Try fallback if primary LLM fails
            if llm_provider == "gemini":
                logger.warning(f"Gemini failed: {email_content['message']}")
                logger.info("Falling back to OpenAI")
                email_content = write_email_with_openai(prompt)
            else:
                logger.warning(f"OpenAI failed: {email_content['message']}")
                logger.info("Falling back to Gemini")
                email_content = write_email_with_gemini(prompt)
                
            # If fallback also failed, return error
            if isinstance(email_content, dict) and "status" in email_content and email_content["status"] == "error":
                logger.error(f"Both LLMs failed to generate email")
                return email_content
        
        # Extract subject and body
        lines = email_content.strip().split("\n")
        subject = ""
        body = ""
        
        # Look for subject line
        for i, line in enumerate(lines):
            if line.lower().startswith("subject:"):
                subject = line[8:].strip()
                body = "\n".join(lines[i+1:]).strip()
                break
        
        # If no subject line found, use the first line as subject and the rest as body
        if not subject:
            if lines:
                subject = lines[0].strip()
                body = "\n".join(lines[1:]).strip()
            else:
                subject = f"Quick question about {company}"
                body = email_content.strip()
        
        # If subject doesn't contain company name, add it
        if company.lower() not in subject.lower():
            subject = f"{subject} - {company}"
        
        # Show the email to the user and ask for approval
        print("\nGenerated Email:")
        print(f"Subject: {subject}")
        print(f"Body:\n{body}")
        
        # Ask user if they want to edit the email
        should_edit = confirm_action("edit this email before proceeding", default=False)
        
        if should_edit:
            # Allow user to edit subject
            new_subject = get_user_input("Edit the subject line (leave empty to keep current):", default=subject)
            if new_subject.strip():
                subject = new_subject.strip()
            
            # Allow user to edit body
            print("\nEdit the email body (type your edited version):")
            print("(Press Enter twice when done)")
            
            lines = []
            while True:
                line = input()
                if not line and lines and not lines[-1]:
                    # Two consecutive empty lines means we're done
                    break
                lines.append(line)
            
            if lines:
                # Remove the last empty line
                if not lines[-1]:
                    lines.pop()
                new_body = "\n".join(lines)
                if new_body.strip():
                    body = new_body
        
        return {
            "status": "success",
            "subject": subject,
            "body": body
        }
    except Exception as e:
        logger.error(f"Error generating email: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to generate email: {str(e)}"
        } 
"""
ICP Generation Module
This module handles extracting and generating Ideal Customer Profile (ICP) information from user prompts.
"""

import os
import re
import json
import logging
from typing import Dict, Any, Optional

# Import interaction tools
try:
    from .interaction import get_user_input, remember, recall, ensure_required_inputs
except ImportError:
    # Handle the case when running directly
    import sys
    import os.path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from tools.interaction import get_user_input, remember, recall, ensure_required_inputs

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_icp_from_prompt(prompt: str) -> Dict[str, Any]:
    """Extract ICP information from a natural language prompt using rule-based approach.
    
    Args:
        prompt: Natural language prompt from the user
        
    Returns:
        Dictionary with extracted ICP information
    """
    # Initialize with default values
    icp = {
        "goal": "Book meetings",
        "industry": None,
        "location": None,
        "role": None,
        "product": None
    }
    
    # Try to extract goal
    if "book" in prompt.lower() and ("meeting" in prompt.lower() or "call" in prompt.lower()):
        icp["goal"] = "Book meetings"
    elif "demo" in prompt.lower():
        icp["goal"] = "Schedule product demos"
    elif "lead" in prompt.lower() or "prospect" in prompt.lower():
        icp["goal"] = "Generate leads"
    
    # Try to extract industry
    industries = ["SaaS", "AI", "Finance", "Healthcare", "Education", "E-commerce", "Retail", "Manufacturing", "Technology"]
    for industry in industries:
        if industry.lower() in prompt.lower():
            icp["industry"] = industry
            break
    
    # Try to extract location
    locations = ["US", "United States", "USA", "Europe", "UK", "Canada", "Australia", "Germany", "France"]
    for location in locations:
        if location.lower() in prompt.lower() or (location == "US" and "us" in prompt.lower().split()):
            icp["location"] = "United States" if location in ["US", "USA"] else location
            break
    
    # Try to extract role
    roles = ["Founder", "CEO", "CTO", "CFO", "COO", "CMO", "VP", "Director", "Manager", "Owner"]
    for role in roles:
        if role.lower() in prompt.lower():
            icp["role"] = role
            break
    
    # Try to extract product info
    product_match = re.search(r"(?:selling|offering|with|about|for|our)\s+([^.]+)", prompt, re.IGNORECASE)
    if product_match:
        icp["product"] = product_match.group(1).strip()
    
    return icp

def extract_icp_with_openai(prompt: str) -> Dict[str, Any]:
    """Extract ICP information using OpenAI.
    
    Args:
        prompt: Natural language prompt from the user
        
    Returns:
        Dictionary with extracted ICP information
    """
    try:
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        model = os.getenv("OPENAI_MODEL", "gpt-4")
        
        system_prompt = """
        Extract the following information from the user's prompt:
        1. Goal (e.g., Book meetings, Generate leads)
        2. Industry (e.g., SaaS, AI, Finance)
        3. Location (e.g., US, Europe)
        4. Role (e.g., Founder, CEO, CTO)
        5. Product description

        Respond in JSON format like this:
        {
            "goal": "Book meetings",
            "industry": "SaaS",
            "location": "United States",
            "role": "Founder",
            "product": "an AI tool that improves sales efficiency"
        }

        If any information is missing, use null for that field.
        """
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        result = response.choices[0].message.content
        
        try:
            return json.loads(result)
        except:
            logger.warning("Failed to parse OpenAI response as JSON. Using rule-based extraction.")
            return extract_icp_from_prompt(prompt)
    except Exception as e:
        logger.error(f"Error using OpenAI for extraction: {e}")
        return extract_icp_from_prompt(prompt)

def extract_icp_with_gemini(prompt: str) -> Dict[str, Any]:
    """Extract ICP information using Gemini.
    
    Args:
        prompt: Natural language prompt from the user
        
    Returns:
        Dictionary with extracted ICP information
    """
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")
        
        system_prompt = """
        Extract the following information from the user's prompt:
        1. Goal (e.g., Book meetings, Generate leads)
        2. Industry (e.g., SaaS, AI, Finance)
        3. Location (e.g., US, Europe)
        4. Role (e.g., Founder, CEO, CTO)
        5. Product description

        Respond in JSON format like this:
        {
            "goal": "Book meetings",
            "industry": "SaaS",
            "location": "United States",
            "role": "Founder",
            "product": "an AI tool that improves sales efficiency"
        }

        If any information is missing, use null for that field.
        """
        
        gemini_model = genai.GenerativeModel(
            model_name=model,
            generation_config={"temperature": 0.2}
        )
        
        response = gemini_model.generate_content([
            {"role": "user", "parts": [{"text": f"{system_prompt}\n\nUser prompt: {prompt}"}]}
        ])
        
        result = response.text if hasattr(response, "text") else ""
        
        # Try to extract JSON from the response
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except:
                logger.warning("Failed to parse Gemini response as JSON. Using rule-based extraction.")
                return extract_icp_from_prompt(prompt)
        else:
            return extract_icp_from_prompt(prompt)
    except Exception as e:
        logger.error(f"Error using Gemini for extraction: {e}")
        return extract_icp_from_prompt(prompt)

def generate_icp(prompt: str, ask_for_missing: bool = True) -> Dict[str, Any]:
    """Generate an Ideal Customer Profile (ICP) from a user prompt.
    
    Args:
        prompt: Natural language prompt from the user
        ask_for_missing: Whether to ask the user for missing information
        
    Returns:
        Dictionary with ICP information
    """
    # Check if we already have ICP information in memory
    icp_recall = recall("icp")
    if icp_recall["status"] == "success":
        logger.info("Using ICP from memory")
        return {
            "status": "success",
            "icp": icp_recall["value"]
        }
    
    # Determine which LLM to use
    llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()
    
    # Extract ICP using the appropriate LLM
    if llm_provider == "gemini":
        logger.info("Extracting ICP with Gemini")
        icp = extract_icp_with_gemini(prompt)
    else:
        logger.info("Extracting ICP with OpenAI")
        icp = extract_icp_with_openai(prompt)
    
    # If extraction failed with primary LLM, try the other one
    if not icp or all(value is None for key, value in icp.items() if key != "goal"):
        if llm_provider == "gemini":
            logger.warning("Gemini extraction failed, trying OpenAI")
            icp = extract_icp_with_openai(prompt)
        else:
            logger.warning("OpenAI extraction failed, trying Gemini")
            icp = extract_icp_with_gemini(prompt)
    
    # If both LLMs failed, use rule-based approach
    if not icp or all(value is None for key, value in icp.items() if key != "goal"):
        logger.warning("LLM extraction failed, using rule-based approach")
        icp = extract_icp_from_prompt(prompt)
    
    # Ask for missing information if needed
    if ask_for_missing:
        if not icp.get("industry"):
            icp["industry"] = get_user_input("What industry are you targeting?", default="SaaS")
        
        if not icp.get("location"):
            icp["location"] = get_user_input("What location are you targeting?", default="United States")
        
        if not icp.get("role"):
            icp["role"] = get_user_input("What role are you targeting?", default="Founder")
        
        if not icp.get("product"):
            icp["product"] = get_user_input("What product/service are you offering?", default="an AI that improves business efficiency")
    
    # Store the ICP in memory
    remember("icp", icp)
    
    return {
        "status": "success",
        "icp": icp
    } 
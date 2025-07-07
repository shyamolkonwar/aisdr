"""
Website Scraping Module
This module handles scraping company websites for personalization data.
"""

import os
import json
import time
import requests
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def scrape_with_firecrawl(url: str) -> Dict[str, Any]:
    """Scrape website using Firecrawl API.
    
    Args:
        url: Website URL to scrape
        
    Returns:
        Dictionary with scraped content or error message
    """
    try:
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            return {"error": "Firecrawl API key not found in environment variables"}
        
        # Prepare the API request
        api_url = "https://api.firecrawl.dev/v1/scrape"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "url": url,
            "elements": [
                {"selector": "h1,h2,h3,p", "type": "text", "name": "content"},
                {"selector": "meta[name='description']", "type": "attribute", "attribute": "content", "name": "meta_description"},
                {"selector": "title", "type": "text", "name": "title"}
            ]
        }
        
        # Make the API request
        response = requests.post(api_url, headers=headers, json=payload)
        data = response.json()
        
        if "error" in data:
            return {"error": f"Firecrawl API error: {data['error']}"}
        
        # Process the results
        content = []
        meta_description = ""
        title = ""
        
        for item in data.get("results", []):
            if item.get("name") == "content":
                content.append(item.get("value", ""))
            elif item.get("name") == "meta_description":
                meta_description = item.get("value", "")
            elif item.get("name") == "title":
                title = item.get("value", "")
        
        # Join all content items
        content_text = " ".join(content)
        
        # Save to local file as backup
        save_scraped_content(url, {
            "title": title,
            "meta_description": meta_description,
            "content": content_text
        })
        
        return {
            "status": "success",
            "url": url,
            "title": title,
            "meta_description": meta_description,
            "content": content_text
        }
    except Exception as e:
        logger.error(f"Firecrawl API error: {str(e)}")
        return {"error": f"Firecrawl API error: {str(e)}"}

def scrape_with_beautifulsoup(url: str) -> Dict[str, Any]:
    """Scrape website using BeautifulSoup.
    
    Args:
        url: Website URL to scrape
        
    Returns:
        Dictionary with scraped content or error message
    """
    try:
        # Try to import required libraries
        try:
            import requests
            from bs4 import BeautifulSoup
        except ImportError:
            return {"error": "BeautifulSoup not installed. Run: pip install beautifulsoup4 requests"}
        
        # Make the request
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Extract title
        title = soup.title.string if soup.title else ""
        
        # Extract meta description
        meta_description = ""
        meta_tag = soup.find("meta", attrs={"name": "description"})
        if meta_tag:
            meta_description = meta_tag.get("content", "")
        
        # Extract main content (headings and paragraphs)
        content = []
        
        # Get headings
        for heading_tag in soup.find_all(["h1", "h2", "h3"]):
            if heading_tag.text.strip():
                content.append(heading_tag.text.strip())
        
        # Get paragraphs
        for p_tag in soup.find_all("p"):
            if p_tag.text.strip():
                content.append(p_tag.text.strip())
        
        # Join all content items
        content_text = " ".join(content)
        
        # Save to local file as backup
        save_scraped_content(url, {
            "title": title,
            "meta_description": meta_description,
            "content": content_text
        })
        
        return {
            "status": "success",
            "url": url,
            "title": title,
            "meta_description": meta_description,
            "content": content_text
        }
    except Exception as e:
        logger.error(f"BeautifulSoup scraping error: {str(e)}")
        return {"error": f"BeautifulSoup scraping error: {str(e)}"}

def save_scraped_content(url: str, content: Dict[str, str]) -> None:
    """Save scraped content to a local file.
    
    Args:
        url: Website URL
        content: Dictionary with scraped content
    """
    try:
        # Create a filename from the URL
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.replace("www.", "")
        
        # Create directory if it doesn't exist
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "websites")
        os.makedirs(data_dir, exist_ok=True)
        
        # Create filename
        filename = os.path.join(data_dir, f"{domain}.json")
        
        # Add timestamp
        content["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
        content["url"] = url
        
        # Write to file
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(content, f, indent=2)
        
        logger.info(f"Saved scraped content to {filename}")
    except Exception as e:
        logger.error(f"Error saving scraped content: {str(e)}")

def get_cached_content(url: str) -> Optional[Dict[str, Any]]:
    """Get cached content for a URL if available.
    
    Args:
        url: Website URL
        
    Returns:
        Dictionary with cached content or None if not found
    """
    try:
        # Create a filename from the URL
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.replace("www.", "")
        
        # Check if file exists
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "websites")
        filename = os.path.join(data_dir, f"{domain}.json")
        
        if not os.path.exists(filename):
            return None
        
        # Read file
        with open(filename, "r", encoding="utf-8") as f:
            content = json.load(f)
        
        # Check if content is too old (older than 7 days)
        if "timestamp" in content:
            timestamp = time.strptime(content["timestamp"], "%Y-%m-%d %H:%M:%S")
            now = time.localtime()
            if (time.mktime(now) - time.mktime(timestamp)) > (7 * 24 * 60 * 60):
                logger.info(f"Cached content for {url} is too old, will re-scrape")
                return None
        
        return content
    except Exception as e:
        logger.error(f"Error reading cached content: {str(e)}")
        return None

def extract_company_info(content: Dict[str, Any]) -> Dict[str, str]:
    """Extract key company information from scraped content.
    
    Args:
        content: Dictionary with scraped content
        
    Returns:
        Dictionary with extracted company information
    """
    # This is a placeholder for more sophisticated extraction
    # In a real implementation, you would use NLP to extract key information
    
    full_text = f"{content.get('title', '')} {content.get('meta_description', '')} {content.get('content', '')}"
    
    # Extract simple company description
    description = content.get('meta_description', '')
    if not description and len(full_text) > 200:
        description = full_text[:200] + "..."
    
    return {
        "company_name": content.get('title', '').split('|')[0].strip() if '|' in content.get('title', '') else content.get('title', ''),
        "description": description,
        "full_content": full_text
    }

def scrape_website(url: str) -> Dict[str, Any]:
    """Main function to scrape a website.
    
    Args:
        url: Website URL to scrape
        
    Returns:
        Dictionary with scraped and processed content
    """
    # Check if we have cached content
    cached_content = get_cached_content(url)
    if cached_content:
        logger.info(f"Using cached content for {url}")
        return {
            "status": "success",
            "url": url,
            "title": cached_content.get("title", ""),
            "meta_description": cached_content.get("meta_description", ""),
            "content": cached_content.get("content", ""),
            "company_info": extract_company_info(cached_content),
            "source": "cache"
        }
    
    # Get the scraper source from environment or use BeautifulSoup as default
    scraper_source = os.getenv("SCRAPER_SOURCE", "beautifulsoup").lower()
    test_mode = os.getenv("TEST_MODE", "false").lower() == "true"
    
    # In test mode, always use BeautifulSoup
    if test_mode:
        logger.info("Running in test mode, using BeautifulSoup")
        result = scrape_with_beautifulsoup(url)
    elif scraper_source == "firecrawl":
        logger.info(f"Scraping {url} with Firecrawl API...")
        result = scrape_with_firecrawl(url)
        
        # If Firecrawl fails, try BeautifulSoup
        if "error" in result:
            logger.warning(f"Firecrawl API failed: {result['error']}")
            logger.info(f"Falling back to BeautifulSoup for {url}...")
            result = scrape_with_beautifulsoup(url)
    else:
        logger.info(f"Scraping {url} with BeautifulSoup...")
        result = scrape_with_beautifulsoup(url)
    
    # If scraping was successful, extract company information
    if "error" not in result:
        result["company_info"] = extract_company_info(result)
    
    return result 
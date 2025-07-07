"""
Lead Generation Module
This module handles finding leads based on the provided ICP.
"""

import os
import csv
import json
import random
import time
import requests
import logging
from typing import Dict, List, Any, Optional

# Import interaction tools
try:
    from tools.interaction import get_user_input, remember, recall, ensure_required_inputs
except ImportError:
    # Handle the case when running directly
    import sys
    import os.path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from tools.interaction import get_user_input, remember, recall, ensure_required_inputs

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_leads_from_apollo(industry: str, role: str, location: str, count: int) -> Dict[str, Any]:
    """Get leads from Apollo.io API.
    
    Args:
        industry: Industry of target leads
        role: Job role/title of target leads
        location: Geographic location of target leads
        count: Number of leads to retrieve
        
    Returns:
        Dictionary with leads or error message
    """
    try:
        api_key = os.getenv("APOLLO_API_KEY")
        if not api_key:
            return {"error": "Apollo API key not found in environment variables"}
        
        url = "https://api.apollo.io/v1/people/search"
        headers = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache"
        }
        
        payload = {
            "api_key": api_key,
            "q_organization_domains": [],
            "page": 1,
            "person_titles": [role],
            "organization_industry_tag_ids": [industry],
            "contact_locations": [location],
            "per_page": count
        }
        
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        
        if "people" not in data:
            return {"error": f"Apollo API error: {data.get('message', 'Unknown error')}"}
        
        leads = []
        for person in data["people"]:
            leads.append({
                "name": f"{person.get('first_name', '')} {person.get('last_name', '')}".strip(),
                "title": person.get("title", ""),
                "company": person.get("organization", {}).get("name", ""),
                "email": person.get("email", ""),
                "linkedin": person.get("linkedin_url", ""),
                "industry": industry,
                "location": person.get("contact_locations", [location])[0] if person.get("contact_locations") else location,
                "website": person.get("organization", {}).get("website_url", "")
            })
        
        # Save to local CSV as backup
        save_leads_to_csv(leads)
        
        return {"status": "success", "count": len(leads), "leads": leads}
    except Exception as e:
        print(f"Apollo API error: {str(e)}")
        return {"error": f"Apollo API error: {str(e)}"}

def get_leads_from_apify(industry: str, role: str, location: str, count: int) -> Dict[str, Any]:
    """Get leads from Apify Apollo.io scraper.
    
    Args:
        industry: Industry of target leads
        role: Job role/title of target leads
        location: Geographic location of target leads
        count: Number of leads to retrieve
        
    Returns:
        Dictionary with leads or error message
    """
    try:
        api_key = os.getenv("APIFY_API_KEY")
        if not api_key:
            return {"error": "Apify API key not found in environment variables"}
        
        # Apify Apollo.io scraper actor
        actor_id = "code_crafter/apollo-io-scraper"
        
        # Build the Apollo.io URL with filters
        # Note: This is a simplified approach - in a real implementation, you would build a more complex URL
        # based on the industry, role, and location parameters
        apollo_url = f"https://app.apollo.io/#/people?sortAscending=false&sortByField=recommendations_score&page=1"
        
        # Add role filter if provided
        if role:
            apollo_url += f"&personTitles[]={role.lower().replace(' ', '+')}"
        
        # Create input for the actor
        input_data = {
            "cleanOutput": False,
            "totalRecords": count,
            "url": apollo_url
        }
        
        # Start the actor and wait for it to finish
        url = f"https://api.apify.com/v2/acts/{actor_id}/runs"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # Start the actor run
        response = requests.post(url, headers=headers, json={"input": input_data})
        run_data = response.json()
        
        if "id" not in run_data:
            return {"error": f"Apify error: {run_data.get('error', {}).get('message', 'Unknown error')}"}
        
        run_id = run_data["id"]
        
        # Wait for the run to finish (poll status)
        status_url = f"https://api.apify.com/v2/acts/{actor_id}/runs/{run_id}"
        max_attempts = 30
        attempts = 0
        
        while attempts < max_attempts:
            status_response = requests.get(status_url, headers=headers)
            status_data = status_response.json()
            
            if status_data.get("status") == "SUCCEEDED":
                break
                
            if status_data.get("status") in ["FAILED", "ABORTED", "TIMED-OUT"]:
                return {"error": f"Apify run failed with status: {status_data.get('status')}"}
                
            attempts += 1
            time.sleep(5)
        
        if attempts >= max_attempts:
            return {"error": "Apify run timed out"}
        
        # Get the results
        dataset_url = f"https://api.apify.com/v2/acts/{actor_id}/runs/{run_id}/dataset/items"
        dataset_response = requests.get(dataset_url, headers=headers)
        items = dataset_response.json()
        
        leads = []
        for item in items:
            # Extract organization data
            org_data = item.get("organization", {})
            
            # Extract website URL
            website_url = org_data.get("website_url", "")
            
            # Extract industry from organization data
            org_industry = org_data.get("industry", industry)
            
            # Get location components
            city = item.get("city", "")
            state = item.get("state", "")
            country = item.get("country", "")
            
            # Combine location components
            lead_location = ", ".join(filter(None, [city, state, country])) or location
            
            leads.append({
                "name": item.get("name", ""),
                "title": item.get("title", ""),
                "company": org_data.get("name", ""),
                "email": item.get("email", ""),
                "linkedin": item.get("linkedin_url", ""),
                "industry": org_industry,
                "location": lead_location,
                "website": website_url
            })
        
        # Save to local CSV as backup
        save_leads_to_csv(leads)
        
        return {"status": "success", "count": len(leads), "leads": leads}
    except Exception as e:
        logger.error(f"Apify error: {str(e)}")
        return {"error": f"Apify error: {str(e)}"}

def get_leads_from_csv(industry: str, role: str, location: str, count: int) -> Dict[str, Any]:
    """Get leads from a local CSV file.
    
    Args:
        industry: Industry filter (optional)
        role: Role filter (optional)
        location: Location filter (optional)
        count: Number of leads to retrieve
        
    Returns:
        Dictionary with leads or error message
    """
    try:
        # Check if sample leads file exists, if not create it
        csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "leads.csv")
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        
        if not os.path.exists(csv_path):
            # Create sample leads file
            create_sample_leads_file(csv_path)
        
        leads = []
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Apply filters if provided
                if (not industry or row["industry"].lower() == industry.lower() or 
                    industry.lower() in row["industry"].lower()):
                    if (not role or row["title"].lower() == role.lower() or 
                        role.lower() in row["title"].lower()):
                        if (not location or row["location"].lower() == location.lower() or
                            location.lower() in row["location"].lower()):
                            leads.append({
                                "name": row["name"],
                                "title": row["title"],
                                "company": row["company"],
                                "email": row["email"],
                                "linkedin": row.get("linkedin", ""),
                                "industry": row.get("industry", industry),
                                "location": row.get("location", location),
                                "website": row.get("website", "")
                            })
                            
                            if len(leads) >= count:
                                break
        
        return {"status": "success", "count": len(leads), "leads": leads}
    except Exception as e:
        print(f"CSV error: {str(e)}")
        return {"error": f"CSV error: {str(e)}"}

def save_leads_to_csv(leads: List[Dict[str, str]]) -> None:
    """Save leads to a local CSV file.
    
    Args:
        leads: List of lead dictionaries
    """
    try:
        csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "leads.csv")
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        
        # Check if file exists to determine if we need to write headers
        file_exists = os.path.exists(csv_path)
        
        # Define fieldnames based on the lead structure
        fieldnames = ["name", "title", "company", "email", "linkedin", "industry", "location", "website"]
        
        # Open file in append mode if it exists, otherwise create it
        mode = "a" if file_exists else "w"
        
        with open(csv_path, mode, newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            # Write header if file is new
            if not file_exists:
                writer.writeheader()
            
            # Write leads
            for lead in leads:
                # Ensure all fields are present
                lead_data = {field: lead.get(field, "") for field in fieldnames}
                writer.writerow(lead_data)
        
        print(f"Saved {len(leads)} leads to {csv_path}")
    except Exception as e:
        print(f"Error saving leads to CSV: {str(e)}")

def create_sample_leads_file(file_path: str) -> None:
    """Create a sample leads CSV file.
    
    Args:
        file_path: Path to create the CSV file
    """
    sample_leads = [
        {
            "name": "Alice Smith",
            "title": "Founder",
            "company": "GrowthAI",
            "email": "alice@growthai.io",
            "linkedin": "https://linkedin.com/in/alicesmith",
            "industry": "AI SaaS",
            "location": "United States",
            "website": "https://growthai.io"
        },
        {
            "name": "Bob Johnson",
            "title": "CTO",
            "company": "TechBoost",
            "email": "bob@techboost.io",
            "linkedin": "https://linkedin.com/in/bobjohnson",
            "industry": "AI SaaS",
            "location": "United States",
            "website": "https://techboost.io"
        },
        {
            "name": "Carol Williams",
            "title": "CEO",
            "company": "DataFlow",
            "email": "carol@dataflow.ai",
            "linkedin": "https://linkedin.com/in/carolwilliams",
            "industry": "AI SaaS",
            "location": "United Kingdom",
            "website": "https://dataflow.ai"
        },
        {
            "name": "David Brown",
            "title": "Founder",
            "company": "AIScale",
            "email": "david@aiscale.io",
            "linkedin": "https://linkedin.com/in/davidbrown",
            "industry": "AI SaaS",
            "location": "Germany",
            "website": "https://aiscale.io"
        },
        {
            "name": "Emma Davis",
            "title": "CEO",
            "company": "NeuralWorks",
            "email": "emma@neuralworks.ai",
            "linkedin": "https://linkedin.com/in/emmadavis",
            "industry": "AI SaaS",
            "location": "France",
            "website": "https://neuralworks.ai"
        },
        {
            "name": "Frank Miller",
            "title": "CTO",
            "company": "AIConnect",
            "email": "frank@aiconnect.io",
            "linkedin": "https://linkedin.com/in/frankmiller",
            "industry": "AI SaaS",
            "location": "Canada",
            "website": "https://aiconnect.io"
        },
        {
            "name": "Grace Wilson",
            "title": "Founder",
            "company": "SmartAI",
            "email": "grace@smartai.tech",
            "linkedin": "https://linkedin.com/in/gracewilson",
            "industry": "AI SaaS",
            "location": "Australia",
            "website": "https://smartai.tech"
        },
        {
            "name": "Henry Taylor",
            "title": "CEO",
            "company": "AIVenture",
            "email": "henry@aiventure.io",
            "linkedin": "https://linkedin.com/in/henrytaylor",
            "industry": "AI SaaS",
            "location": "Singapore",
            "website": "https://aiventure.io"
        },
        {
            "name": "Irene Clark",
            "title": "Founder",
            "company": "BrainTech",
            "email": "irene@braintech.ai",
            "linkedin": "https://linkedin.com/in/ireneclark",
            "industry": "AI SaaS",
            "location": "Netherlands",
            "website": "https://braintech.ai"
        },
        {
            "name": "Jack Roberts",
            "title": "CTO",
            "company": "IntelliSoft",
            "email": "jack@intellisoft.io",
            "linkedin": "https://linkedin.com/in/jackroberts",
            "industry": "AI SaaS",
            "location": "Sweden",
            "website": "https://intellisoft.io"
        }
    ]
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "title", "company", "email", "linkedin", "industry", "location", "website"])
        writer.writeheader()
        writer.writerows(sample_leads)

def get_leads(industry: str, role: str, location: str, count: int = None) -> Dict[str, Any]:
    """Main function to get leads based on ICP.
    
    Prioritizes Apollo API, then falls back to Apify.
    
    Args:
        industry: Industry of target leads
        role: Job role/title of target leads
        location: Geographic location of target leads
        count: Number of leads to retrieve
        
    Returns:
        Dictionary with leads or error message
    """
    # Check if count is specified, if not ask the user
    if count is None:
        # First try to recall from memory
        count_recall = recall("leads_count")
        if count_recall.get("status") == "success":
            count = int(count_recall["value"])
            logger.info(f"Using remembered lead count: {count}")
        else:
            # Ask the user how many leads they want
            count_input = get_user_input(
                f"How many {industry} {role} leads from {location} would you like to find?", 
                default="5"
            )
            try:
                count = int(count_input)
                # Remember for future use
                remember("leads_count", count)
                logger.info(f"User requested {count} leads")
            except (ValueError, TypeError):
                count = 5
                logger.warning(f"Invalid count input, using default: {count}")

    # In test mode, always use the sample CSV data
    if os.getenv("TEST_MODE", "false").lower() == "true":
        logger.info("Running in test mode, using sample CSV data")
        return get_leads_from_csv(industry, role, location, count)

    # 1. Try Apollo first
    logger.info("Attempting to fetch leads from Apollo.io API...")
    apollo_result = get_leads_from_apollo(industry, role, location, count)
    if apollo_result.get("status") == "success" and apollo_result.get("leads"):
        logger.info(f"Successfully fetched {apollo_result.get('count')} leads from Apollo.")
        return apollo_result

    # 2. If Apollo fails, fall back to Apify
    logger.warning(f"Apollo API failed: {apollo_result.get('error', 'No leads returned')}")
    logger.info("Falling back to Apify Apollo scraper...")
    apify_result = get_leads_from_apify(industry, role, location, count)
    if apify_result.get("status") == "success" and apify_result.get("leads"):
        logger.info(f"Successfully fetched {apify_result.get('count')} leads from Apify.")
        return apify_result

    # 3. If both fail, return an error
    logger.error("Both Apollo and Apify failed to retrieve leads.")
    return {"error": "Failed to retrieve leads from all available sources (Apollo, Apify)."} 
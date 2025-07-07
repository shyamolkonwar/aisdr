#!/usr/bin/env python3
"""
AI SDR Agent - Main Entry Point
This script initializes and runs the autonomous AI SDR agent.
"""

import os
import argparse
import json
import logging
from dotenv import load_dotenv
from planner import AgentPlanner

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), "logs", "ai_sdr_agent.log"), mode='a'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="AI SDR Agent")
    parser.add_argument("--config", type=str, default="config.json", help="Path to configuration file")
    parser.add_argument("--mode", type=str, default="interactive", choices=["auto", "interactive", "test"], 
                        help="Run mode: auto, interactive, or test")
    return parser.parse_args()

def load_config(config_path):
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Config file not found: {config_path}")
        return create_default_config(config_path)

def create_default_config(config_path):
    """Create a default configuration file."""
    default_config = {
        "lead_source": "csv",  # Options: apollo, apify, csv
        "email_provider": "gmail",  # Options: gmail, mailersend, sendgrid, lemlist
        "crm": "local_csv",  # Options: airtable, supabase, notion, google_sheets, local_csv
    }
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    with open(config_path, 'w') as f:
        json.dump(default_config, f, indent=2)
    
    logger.info(f"Created default config at {config_path}")
    return default_config

def get_llm_client():
    """Get a Deepseek LLM client."""
    if not os.getenv("DEEPSEEK_API_KEY"):
        logger.error("DEEPSEEK_API_KEY not found in .env file.")
        return None
    
    try:
        import openai
        client = openai.OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com/v1"
        )
        os.environ["LLM_PROVIDER"] = "deepseek"
        logger.info("Using Deepseek as the LLM provider")
        return client
    except Exception as e:
        logger.error(f"Error initializing Deepseek client: {e}")
        return None

def main():
    """Main entry point for the AI SDR agent."""
    # Ensure logs directory exists
    os.makedirs(os.path.join(os.path.dirname(__file__), "logs"), exist_ok=True)
    
    # Ensure data directories exist
    os.makedirs(os.path.join(os.path.dirname(__file__), "data"), exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), "data", "leads"), exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), "data", "emails"), exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), "data", "websites"), exist_ok=True)
    
    args = parse_args()
    config = load_config(args.config)
    
    # Get user prompt
    print("What would you like the AI SDR agent to do?")
    user_prompt = input("> ")
    
    logger.info(f"Starting AI SDR Agent with prompt: {user_prompt}")
    
    # Get LLM client
    llm_client = get_llm_client()
    if not llm_client:
        return

    llm_provider = "deepseek"
    
    # Initialize the agent planner
    planner = AgentPlanner(config, mode=args.mode, user_prompt=user_prompt, llm_client=llm_client, llm_provider=llm_provider)
    
    # Run the agent
    planner.run()

if __name__ == "__main__":
    main() 
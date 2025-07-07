"""
User Interaction Module
This module handles user interaction, memory storage, and input validation.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List, Union

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global memory store for the session
_memory_store = {}

def get_user_input(prompt: str, default: str = None, options: List[str] = None) -> str:
    """Get input from the user via console.
    
    Args:
        prompt: Question or prompt to show the user
        default: Default value if user provides no input
        options: List of valid options (if provided, input must be one of these)
        
    Returns:
        User's input as string
    """
    # Format the prompt with options if provided
    display_prompt = prompt
    
    if options:
        option_str = "/".join(options)
        display_prompt = f"{prompt} ({option_str})"
    
    if default:
        display_prompt = f"{display_prompt} [default: {default}]"
    
    # Add the input indicator
    display_prompt = f"{display_prompt}: "
    
    while True:
        user_input = input(display_prompt).strip()
        
        # Use default if no input provided
        if not user_input and default:
            logger.info(f"Using default value: {default}")
            return default
        
        # Validate against options if provided
        if options and user_input not in options:
            print(f"Invalid input. Please choose one of: {', '.join(options)}")
            continue
        
        # If we got here, input is valid
        return user_input

def remember(key: str, value: Any) -> Dict[str, Any]:
    """Store a value in memory for later use.
    
    Args:
        key: Key to store the value under
        value: Value to store
        
    Returns:
        Dictionary with status and stored value
    """
    global _memory_store
    
    try:
        # Store the value
        _memory_store[key] = value
        
        # Also persist to disk for longer-term storage
        memory_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "memory.json")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(memory_file), exist_ok=True)
        
        # Load existing memory if available
        disk_memory = {}
        if os.path.exists(memory_file):
            try:
                with open(memory_file, 'r') as f:
                    disk_memory = json.load(f)
            except:
                disk_memory = {}
        
        # Update and save
        disk_memory[key] = value
        with open(memory_file, 'w') as f:
            json.dump(disk_memory, f, indent=2, default=str)
        
        logger.info(f"Stored value for key: {key}")
        
        return {
            "status": "success",
            "key": key,
            "value": value
        }
    except Exception as e:
        logger.error(f"Failed to store value: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to store value: {str(e)}"
        }

def recall(key: str, default: Any = None) -> Dict[str, Any]:
    """Retrieve a value from memory.
    
    Args:
        key: Key to retrieve
        default: Default value if key not found
        
    Returns:
        Dictionary with status and retrieved value
    """
    global _memory_store
    
    try:
        # Check in-memory store first
        if key in _memory_store:
            logger.info(f"Retrieved value for key from memory: {key}")
            return {
                "status": "success",
                "key": key,
                "value": _memory_store[key],
                "source": "memory"
            }
        
        # Check disk storage
        memory_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "memory.json")
        
        if os.path.exists(memory_file):
            try:
                with open(memory_file, 'r') as f:
                    disk_memory = json.load(f)
                    
                if key in disk_memory:
                    # Update in-memory store
                    _memory_store[key] = disk_memory[key]
                    
                    logger.info(f"Retrieved value for key from disk: {key}")
                    return {
                        "status": "success",
                        "key": key,
                        "value": disk_memory[key],
                        "source": "disk"
                    }
            except:
                pass
        
        # Key not found, return default if provided
        if default is not None:
            logger.info(f"Key not found, using default value: {key}")
            return {
                "status": "success",
                "key": key,
                "value": default,
                "source": "default"
            }
        
        # Key not found and no default
        logger.warning(f"Key not found in memory: {key}")
        return {
            "status": "error",
            "message": f"Key not found: {key}"
        }
    except Exception as e:
        logger.error(f"Failed to retrieve value: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to retrieve value: {str(e)}"
        }

def ensure_required_inputs(required_inputs: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Ensure all required inputs are available, prompting the user if needed.
    
    Args:
        required_inputs: Dictionary of required inputs with their properties
            Format: {
                "input_name": {
                    "prompt": "Question to ask user",
                    "default": "Default value",
                    "options": ["option1", "option2"],  # Optional list of valid options
                    "type": "str"  # Optional type conversion (str, int, float, bool)
                }
            }
        
    Returns:
        Dictionary with all required inputs
    """
    result = {}
    
    for input_name, properties in required_inputs.items():
        # Check if we already have this input in memory
        recall_result = recall(input_name)
        
        if recall_result["status"] == "success":
            # We have it in memory
            result[input_name] = recall_result["value"]
            logger.info(f"Using remembered value for {input_name}: {result[input_name]}")
        else:
            # We need to ask the user
            prompt = properties.get("prompt", f"Please enter {input_name}")
            default = properties.get("default")
            options = properties.get("options")
            
            # Get input from user
            user_input = get_user_input(prompt, default, options)
            
            # Convert type if specified
            input_type = properties.get("type", "str")
            if input_type == "int":
                try:
                    user_input = int(user_input)
                except:
                    logger.warning(f"Could not convert {input_name} to int, using as string")
            elif input_type == "float":
                try:
                    user_input = float(user_input)
                except:
                    logger.warning(f"Could not convert {input_name} to float, using as string")
            elif input_type == "bool":
                user_input = user_input.lower() in ["true", "yes", "y", "1"]
            
            # Store the input
            result[input_name] = user_input
            remember(input_name, user_input)
            
            logger.info(f"Collected and stored value for {input_name}: {user_input}")
    
    return {
        "status": "success",
        "inputs": result
    }

def confirm_action(action_description: str, default: bool = False) -> bool:
    """Ask the user to confirm an action.
    
    Args:
        action_description: Description of the action to confirm
        default: Default response (True for yes, False for no)
        
    Returns:
        Boolean indicating whether the action was confirmed
    """
    default_str = "Y/n" if default else "y/N"
    response = get_user_input(f"Do you want to {action_description}? {default_str}")
    
    if not response:
        return default
    
    return response.lower() in ["y", "yes", "true", "1"]

def clear_memory() -> Dict[str, Any]:
    """Clear all stored memory.
    
    Returns:
        Dictionary with status
    """
    global _memory_store
    
    try:
        # Clear in-memory store
        _memory_store = {}
        
        # Clear disk storage
        memory_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "memory.json")
        
        if os.path.exists(memory_file):
            with open(memory_file, 'w') as f:
                json.dump({}, f)
        
        logger.info("Memory cleared")
        
        return {
            "status": "success",
            "message": "Memory cleared"
        }
    except Exception as e:
        logger.error(f"Failed to clear memory: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to clear memory: {str(e)}"
        } 
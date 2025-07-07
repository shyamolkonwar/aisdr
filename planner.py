
"""
Agent Planner Module
This module handles the orchestration of the AI SDR agent workflow using Deepseek.
"""

import os
import time
import json
import openai
from typing import Dict, List, Any

# Import tool modules
from tools.get_leads import get_leads
from tools.scrape_website import scrape_website
from tools.write_email import write_email
from tools.send_email import send_email
from tools.log_to_crm import log_to_crm
from tools.generate_icp import generate_icp
from tools.interaction import get_user_input, remember, recall, ensure_required_inputs, confirm_action
from task_manager import TaskManager

class AgentPlanner:
    """Agent Planner class that orchestrates the AI SDR agent workflow."""
    
    def __init__(self, config: Dict[str, Any], mode: str = "interactive", user_prompt: str = None, llm_client: any = None, llm_provider: str = "deepseek"):
        """Initialize the Agent Planner.
        
        Args:
            config: Configuration dictionary with settings
            mode: Operation mode ("auto" or "interactive")
            user_prompt: Original user prompt for task planning
            llm_client: Pre-configured LLM client for Deepseek
            llm_provider: Name of the LLM provider (should be 'deepseek')
        """
        self.config = config
        self.mode = mode
        self.user_prompt = user_prompt or "Help me with sales outreach"
        self.chat_history = []
        self.leads = []
        
        # Set LLM client and provider
        self.llm_provider = llm_provider
        self.llm_client = llm_client
        self.llm_model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        
        print(f"Using LLM provider: {self.llm_provider} with model: {self.llm_model}")
        
        # Initialize task manager
        self.task_manager = TaskManager(config, self.llm_client, self.llm_provider)
        
        # Define available functions
        self.functions = [
            {
                "type": "function",
                "function": {
                    "name": "get_leads",
                    "description": "Find leads matching the Ideal Customer Profile (ICP)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "industry": {"type": "string", "description": "Industry of target leads"},
                            "role": {"type": "string", "description": "Job role/title of target leads"},
                            "location": {"type": "string", "description": "Geographic location of target leads"},
                            "count": {"type": "integer", "description": "Number of leads to retrieve"}
                        },
                        "required": ["industry", "role", "location"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "scrape_website",
                    "description": "Scrape company website content for personalization",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string", "description": "Website URL to scrape"}
                        },
                        "required": ["url"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "write_email",
                    "description": "Write a personalized cold email to a prospect",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Recipient's name"},
                            "title": {"type": "string", "description": "Recipient's job title"},
                            "company": {"type": "string", "description": "Recipient's company"},
                            "industry": {"type": "string", "description": "Recipient's industry"},
                            "product_description": {"type": "string", "description": "Description of your product/service"},
                            "website": {"type": "string", "description": "Company website URL for personalization (optional)"}
                        },
                        "required": ["name", "title", "company", "industry", "product_description"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "send_email",
                    "description": "Send an email to a prospect",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "recipient_email": {"type": "string", "description": "Recipient's email address"},
                            "subject": {"type": "string", "description": "Email subject line"},
                            "body": {"type": "string", "description": "Email body content"}
                        },
                        "required": ["recipient_email", "subject", "body"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "log_to_crm",
                    "description": "Log lead and interaction details to CRM",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Lead's name"},
                            "email": {"type": "string", "description": "Lead's email address"},
                            "company": {"type": "string", "description": "Lead's company"},
                            "status": {"type": "string", "description": "Current status (e.g., sent, replied, bounced)"},
                            "notes": {"type": "string", "description": "Additional notes about the interaction"}
                        },
                        "required": ["name", "email", "company", "status"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_icp",
                    "description": "Generate an Ideal Customer Profile (ICP) from a user prompt",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string", "description": "User prompt to extract ICP from"},
                            "ask_for_missing": {"type": "boolean", "description": "Whether to ask the user for missing information"}
                        },
                        "required": ["prompt"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Add a new task to the task list",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string", "description": "Description of the task"},
                            "dependencies": {"type": "array", "items": {"type": "string"}, "description": "List of task IDs that must be completed before this task"}
                        },
                        "required": ["description"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "complete_task",
                    "description": "Mark a task as completed",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "string", "description": "ID of the task to mark as completed"}
                        },
                        "required": ["task_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "add_task_note",
                    "description": "Add a note to a task",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "string", "description": "ID of the task to add a note to"},
                            "note": {"type": "string", "description": "Note to add to the task"}
                        },
                        "required": ["task_id", "note"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_tasks",
                    "description": "Get the current task list",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_user_input",
                    "description": "Get input from the user via console",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string", "description": "Question or prompt to show the user"},
                            "default": {"type": "string", "description": "Default value if user provides no input"},
                            "options": {"type": "array", "items": {"type": "string"}, "description": "List of valid options"}
                        },
                        "required": ["prompt"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "remember",
                    "description": "Store a value in memory for later use",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "key": {"type": "string", "description": "Key to store the value under"},
                            "value": {"type": "string", "description": "Value to store"}
                        },
                        "required": ["key", "value"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "recall",
                    "description": "Retrieve a value from memory",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "key": {"type": "string", "description": "Key to retrieve"},
                            "default": {"type": "string", "description": "Default value if key not found"}
                        },
                        "required": ["key"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "ensure_required_inputs",
                    "description": "Ensure all required inputs are available, prompting the user if needed",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "required_inputs": {
                                "type": "object",
                                "description": "Dictionary of required inputs with their properties"
                            }
                        },
                        "required": ["required_inputs"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "confirm_action",
                    "description": "Ask the user to confirm an action",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action_description": {"type": "string", "description": "Description of the action to confirm"},
                            "default": {"type": "boolean", "description": "Default response (true for yes, false for no)"}
                        },
                        "required": ["action_description"]
                    }
                }
            }
        ]
        
        # Initialize system prompt
        self.system_prompt = f"""You are an autonomous AI SDR agent that helps with sales outreach tasks.

You have access to the following tools:
1. generate_icp: Generate an Ideal Customer Profile (ICP) from the user's prompt
2. get_leads: Find leads matching the Ideal Customer Profile (ICP)
3. scrape_website: Scrape company website content for personalization
4. write_email: Write a personalized cold email to a prospect
5. send_email: Send an email to a prospect
6. log_to_crm: Log lead and interaction details to CRM

You also have tools for user interaction:
- get_user_input: Ask the user for specific information
- remember: Store values for future use
- recall: Retrieve stored values
- ensure_required_inputs: Check if you have all required information, prompting the user if needed
- confirm_action: Ask the user to confirm before taking important actions

You also have a task management system. Before performing any action, you should:
1. Think about what tasks need to be done based on the user's request
2. Add tasks using the add_task function
3. Mark tasks as completed using the complete_task function
4. Add notes to tasks using the add_task_note function

DO NOT make assumptions about what the user wants. If you need more information, use get_user_input to ask.

IMPORTANT: Always get user confirmation before sending emails or making important decisions.

Think step by step and work through tasks methodically.
"""

    def add_message(self, role: str, content: str, name: str = None) -> None:
        """Add a message to the chat history.
        
        Args:
            role: Message role (system, user, assistant, function)
            content: Message content
            name: Function name (required for function role)
        """
        message = {"role": role, "content": content}
        if role == "function" and name:
            message["name"] = name
        self.chat_history.append(message)
    
    def call_function(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a function by name with the provided arguments.
        
        Args:
            function_name: Name of the function to call
            arguments: Function arguments
            
        Returns:
            Function result
        """
        function_map = {
            "get_leads": get_leads,
            "scrape_website": scrape_website,
            "write_email": write_email,
            "send_email": send_email,
            "log_to_crm": log_to_crm,
            "generate_icp": generate_icp,
            "add_task": self.task_manager.add_task,
            "complete_task": lambda task_id: self.task_manager.complete_task(task_id),
            "add_task_note": lambda task_id, note: self.task_manager.add_task_note(task_id, note),
            "get_tasks": lambda: self.task_manager.get_tasks_as_dict(),
            "get_user_input": get_user_input,
            "remember": remember,
            "recall": recall,
            "ensure_required_inputs": ensure_required_inputs,
            "confirm_action": confirm_action
        }
        
        if function_name in function_map:
            # Always ask for confirmation before sending emails
            if function_name == "send_email":
                print("\nAbout to send email:")
                print(f"To: {arguments['recipient_email']}")
                print(f"Subject: {arguments['subject']}")
                print(f"Body:\n{arguments['body']}")
                
                should_send = confirm_action("send this email", default=False)
                if not should_send:
                    return {"status": "cancelled", "message": "Email sending cancelled by user"}
            
            # Call the actual function
            return function_map[function_name](**arguments)
        else:
            return {"error": f"Function {function_name} not found"}
    
    def get_next_action(self) -> Dict:
        """Get next action from the Deepseek LLM."""
        try:
            # Convert chat history to Deepseek format
            deepseek_messages = []
            for msg in self.chat_history:
                if msg["role"] == "system":
                    continue  # Prepend to first user message
                elif msg["role"] == "function":
                    deepseek_messages.append({"role": "assistant", "content": f"Function response: {msg['content']}"})
                else:
                    role = "user" if msg["role"] == "user" else "assistant"
                    deepseek_messages.append({"role": role, "content": msg["content"]})

            # Add system prompt to first user message
            if deepseek_messages and deepseek_messages[0]["role"] == "user":
                for msg in self.chat_history:
                    if msg["role"] == "system":
                        deepseek_messages[0]["content"] = f"{msg['content']}\n\n{deepseek_messages[0]['content']}"
                        break

            # Call Deepseek API
            response = self.llm_client.chat.completions.create(
                model=self.llm_model,
                messages=deepseek_messages,
                tools=self.functions,
                tool_choice="auto",
                temperature=0.2
            )

            message = response.choices[0].message
            self.add_message("assistant", message.content if message.content else "")

            # Check for function calls
            if hasattr(message, 'tool_calls') and message.tool_calls:
                tool_call = message.tool_calls[0]
                return {
                    "function_call": True,
                    "function_name": tool_call.function.name,
                    "function_args": json.loads(tool_call.function.arguments),
                    "message": message.content
                }
            else:
                return {
                    "function_call": False,
                    "message": message.content
                }
        except Exception as e:
            print(f"Error with Deepseek API: {str(e)}")
            return {
                "function_call": False,
                "message": "I'm having trouble connecting to the Deepseek API. Please check your API key and try again."
            }
    
    def run(self) -> None:
        """Run the agent planner workflow."""
        print(f"Starting AI SDR Agent in {self.mode} mode")
        
        # Ensure data directories exist
        os.makedirs(os.path.join(os.path.dirname(__file__), "data"), exist_ok=True)
        
        # Initialize chat with system prompt
        self.add_message("system", self.system_prompt)
        self.add_message("user", f"I need help with the following: {self.user_prompt}")
        
        max_turns = 50  # Safety limit
        for i in range(max_turns):
            try:
                # Get next action from LLM
                action = self.get_next_action()
                
                # Check if function call is requested
                if action.get("function_call"):
                    function_name = action["function_name"]
                    function_args = action["function_args"]
                    
                    print(f"\nExecuting: {function_name}")
                    if self.mode == "interactive":
                        print(f"Arguments: {json.dumps(function_args, indent=2)}")
                    
                    # Call the function
                    function_response = self.call_function(function_name, function_args)
                    
                    # Add function response to chat history
                    self.add_message(
                        "function", 
                        json.dumps(function_response),
                        name=function_name
                    )
                    
                    # If we got leads, store them
                    if function_name == "get_leads" and isinstance(function_response, dict) and "leads" in function_response:
                        self.leads = function_response["leads"]
                    
                else:
                    # No function call, so print the assistant's message
                    print(f"\nAssistant: {action.get('message')}")

                    # Check for completion
                    if action.get("message") and ("completed" in action["message"].lower() or "finished" in action["message"].lower()):
                        print("\nAgent has completed its tasks.")
                        break
                    
                    tasks_result = self.task_manager.get_tasks_as_dict()
                    if tasks_result.get("count", 0) > 0 and tasks_result.get("completed") == tasks_result.get("count"):
                        print("\nAll tasks have been completed.")
                        break

                # Add a small delay between actions
                time.sleep(1)

            except Exception as e:
                print(f"Error during agent execution: {str(e)}")
                if self.mode == "interactive":
                    user_input = input("\nEncountered an error. Continue? (y/n): ")
                    if user_input.lower() != 'y':
                        break
                else:
                    # In auto mode, stop on error
                    break
            
            if i == max_turns - 1:
                print("\nReached max turns. Ending session.")
        
        print("\nAI SDR Agent workflow completed.")

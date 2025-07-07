"""
Task Manager Module
This module handles task planning, execution, and tracking for the AI SDR agent.
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum
import re

class TaskStatus(Enum):
    """Task status enum."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class Task:
    """Task class representing a single task in the workflow."""
    
    def __init__(self, id: str, description: str, dependencies: List[str] = None):
        """Initialize a task.
        
        Args:
            id: Unique identifier for the task
            description: Description of the task
            dependencies: List of task IDs that must be completed before this task
        """
        self.id = id
        self.description = description
        self.dependencies = dependencies or []
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.notes = []
    
    def start(self):
        """Mark the task as in progress."""
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.now()
    
    def complete(self):
        """Mark the task as completed."""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
    
    def fail(self, reason: str):
        """Mark the task as failed.
        
        Args:
            reason: Reason for failure
        """
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.now()
        self.add_note(f"Failed: {reason}")
    
    def skip(self, reason: str):
        """Mark the task as skipped.
        
        Args:
            reason: Reason for skipping
        """
        self.status = TaskStatus.SKIPPED
        self.completed_at = datetime.now()
        self.add_note(f"Skipped: {reason}")
    
    def add_note(self, note: str):
        """Add a note to the task.
        
        Args:
            note: Note to add
        """
        self.notes.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content": note
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary.
        
        Returns:
            Dictionary representation of the task
        """
        return {
            "id": self.id,
            "description": self.description,
            "dependencies": self.dependencies,
            "status": self.status.value,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "started_at": self.started_at.strftime("%Y-%m-%d %H:%M:%S") if self.started_at else None,
            "completed_at": self.completed_at.strftime("%Y-%m-%d %H:%M:%S") if self.completed_at else None,
            "notes": self.notes
        }

class TaskManager:
    """Task Manager class that handles task planning, execution, and tracking."""
    
    def __init__(self, config: Dict[str, Any], llm_client=None, llm_provider: str = "openai"):
        """Initialize the Task Manager.
        
        Args:
            config: Configuration dictionary with settings
            llm_client: LLM client (OpenAI or Gemini)
            llm_provider: LLM provider name
        """
        self.config = config
        self.llm_client = llm_client
        self.llm_provider = llm_provider
        self.tasks = {}
        self.task_log_file = os.path.join(os.path.dirname(__file__), "logs", "tasks.md")
        self.ensure_log_directory()
    
    def ensure_log_directory(self):
        """Ensure the log directory exists."""
        log_dir = os.path.dirname(self.task_log_file)
        os.makedirs(log_dir, exist_ok=True)
    
    def generate_tasks_with_llm(self, prompt: str) -> List[Task]:
        """Generate tasks using LLM.
        
        Args:
            prompt: User prompt
            
        Returns:
            List of generated tasks
        """
        system_prompt = """
        You are an AI SDR (Sales Development Representative) agent. Based on the user's prompt, create a detailed task list for outreach.
        Break down the process into specific, actionable tasks with dependencies.
        
        Respond with a JSON array of tasks in this format:
        [
            {
                "id": "task-1",
                "description": "Analyze user prompt to determine outreach goals",
                "dependencies": []
            },
            {
                "id": "task-2",
                "description": "Generate Ideal Customer Profile (ICP) based on user needs",
                "dependencies": ["task-1"]
            },
            ...
        ]
        
        Include tasks for:
        1. Analyzing the user prompt
        2. Generating an Ideal Customer Profile (ICP) if needed
        3. Finding leads matching the ICP
        4. Researching each lead
        5. Writing personalized emails
        6. Getting user approval before sending emails
        7. Sending emails
        8. Logging interactions in CRM
        
        Be specific and detailed. Create tasks based on what the user is asking for.
        """
        
        try:
            if self.llm_provider == "openai":
                import openai
                response = self.llm_client.chat.completions.create(
                    model=os.getenv("OPENAI_MODEL", "gpt-4"),
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"User prompt: {prompt}"}
                    ],
                    temperature=0.2
                )
                result = response.choices[0].message.content
                
                # Extract JSON from response
                json_match = re.search(r'\[.*\]', result, re.DOTALL)
                if json_match:
                    task_data = json.loads(json_match.group(0))
                    return [Task(t["id"], t["description"], t.get("dependencies", [])) for t in task_data]
            
            elif self.llm_provider == "gemini":
                model = self.llm_client.GenerativeModel(
                    model_name=os.getenv("GEMINI_MODEL", "gemini-2.5-pro"),
                    generation_config={"temperature": 0.2}
                )
                response = model.generate_content([
                    {"role": "user", "parts": [{"text": f"{system_prompt}\n\nUser prompt: {prompt}"}]}
                ])
                result = response.text
                
                # Extract JSON from response
                json_match = re.search(r'\[.*\]', result, re.DOTALL)
                if json_match:
                    task_data = json.loads(json_match.group(0))
                    return [Task(t["id"], t["description"], t.get("dependencies", [])) for t in task_data]
        
        except Exception as e:
            print(f"Error generating tasks with LLM: {e}")
        
        # Fallback to default tasks
        return self.generate_default_tasks(prompt)
    
    def generate_default_tasks(self, prompt: str) -> List[Task]:
        """Generate default tasks based on the user prompt.
        
        Args:
            prompt: User prompt
            
        Returns:
            List of default tasks
        """
        tasks = [
            Task("task-1", "Analyze user prompt to determine outreach goals", []),
            Task("task-2", "Generate Ideal Customer Profile (ICP) based on user needs", ["task-1"]),
            Task("task-3", "Find leads matching the ICP", ["task-2"]),
            Task("task-4", "Research each lead for personalization", ["task-3"]),
            Task("task-5", "Write personalized cold emails for each lead", ["task-4"]),
            Task("task-6", "Get user approval for emails", ["task-5"]),
            Task("task-7", "Send emails to leads", ["task-6"]),
            Task("task-8", "Log interactions in CRM", ["task-7"])
        ]
        return tasks
    
    def get_next_task(self) -> Optional[Dict[str, Any]]:
        """Get the next task to execute.
        
        Returns:
            Next task as dictionary or None if no tasks are available
        """
        # Find tasks that are ready to execute (all dependencies completed)
        ready_tasks = []
        for task_id, task in self.tasks.items():
            if task.status == TaskStatus.PENDING:
                dependencies_met = True
                for dep_id in task.dependencies:
                    if dep_id not in self.tasks or self.tasks[dep_id].status != TaskStatus.COMPLETED:
                        dependencies_met = False
                        break
                
                if dependencies_met:
                    ready_tasks.append(task)
        
        # Sort by ID to maintain order
        ready_tasks.sort(key=lambda t: t.id)
        
        if ready_tasks:
            return ready_tasks[0].to_dict()
        
        return None
    
    def start_task(self, task_id: str) -> Dict[str, Any]:
        """Start a task.
        
        Args:
            task_id: ID of the task to start
            
        Returns:
            Dictionary with status and task
        """
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.start()
            self.write_tasks_to_log()
            return {"status": "success", "task": task.to_dict()}
        else:
            return {"status": "error", "message": f"Task {task_id} not found"}
    
    def complete_task(self, task_id: str) -> Dict[str, Any]:
        """Complete a task.
        
        Args:
            task_id: ID of the task to complete
            
        Returns:
            Dictionary with status and task
        """
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.complete()
            self.write_tasks_to_log()
            return {"status": "success", "task": task.to_dict()}
        else:
            return {"status": "error", "message": f"Task {task_id} not found"}
    
    def fail_task(self, task_id: str, reason: str) -> Dict[str, Any]:
        """Mark a task as failed.
        
        Args:
            task_id: ID of the task to fail
            reason: Reason for failure
            
        Returns:
            Dictionary with status and task
        """
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.fail(reason)
            self.write_tasks_to_log()
            return {"status": "success", "task": task.to_dict()}
        else:
            return {"status": "error", "message": f"Task {task_id} not found"}
    
    def skip_task(self, task_id: str, reason: str) -> Dict[str, Any]:
        """Mark a task as skipped.
        
        Args:
            task_id: ID of the task to skip
            reason: Reason for skipping
            
        Returns:
            Dictionary with status and task
        """
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.skip(reason)
            self.write_tasks_to_log()
            return {"status": "success", "task": task.to_dict()}
        else:
            return {"status": "error", "message": f"Task {task_id} not found"}
    
    def add_task_note(self, task_id: str, note: str) -> Dict[str, Any]:
        """Add a note to a task.
        
        Args:
            task_id: ID of the task to add a note to
            note: Note to add
            
        Returns:
            Dictionary with status and task
        """
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.add_note(note)
            self.write_tasks_to_log()
            return {"status": "success", "task": task.to_dict()}
        else:
            return {"status": "error", "message": f"Task {task_id} not found"}
    
    def add_task(self, description: str, dependencies: List[str] = None) -> Dict[str, Any]:
        """Add a new task.
        
        Args:
            description: Description of the task
            dependencies: List of task IDs that must be completed before this task
            
        Returns:
            Dictionary with status and task
        """
        # Generate a new task ID
        task_id = f"task-{len(self.tasks) + 1}"
        
        # Create the task
        task = Task(task_id, description, dependencies)
        
        # Add to tasks
        self.tasks[task_id] = task
        
        # Write tasks to log file
        self.write_tasks_to_log()
        
        return {"status": "success", "task": task.to_dict()}
    
    def write_tasks_to_log(self):
        """Write tasks to log file."""
        try:
            with open(self.task_log_file, "w") as f:
                f.write("# Task Log\n\n")
                f.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Write task summary
                f.write("## Task Summary\n\n")
                
                total_tasks = len(self.tasks)
                completed_tasks = sum(1 for task in self.tasks.values() if task.status == TaskStatus.COMPLETED)
                in_progress_tasks = sum(1 for task in self.tasks.values() if task.status == TaskStatus.IN_PROGRESS)
                pending_tasks = sum(1 for task in self.tasks.values() if task.status == TaskStatus.PENDING)
                failed_tasks = sum(1 for task in self.tasks.values() if task.status == TaskStatus.FAILED)
                skipped_tasks = sum(1 for task in self.tasks.values() if task.status == TaskStatus.SKIPPED)
                
                f.write(f"- Total Tasks: {total_tasks}\n")
                f.write(f"- Completed: {completed_tasks}\n")
                f.write(f"- In Progress: {in_progress_tasks}\n")
                f.write(f"- Pending: {pending_tasks}\n")
                f.write(f"- Failed: {failed_tasks}\n")
                f.write(f"- Skipped: {skipped_tasks}\n")
                
                f.write("\n## Tasks\n\n")
                
                # Sort tasks by ID
                sorted_tasks = sorted(self.tasks.values(), key=lambda t: t.id)
                
                for task in sorted_tasks:
                    # Write task header
                    status_emoji = {
                        TaskStatus.PENDING: "⏳",
                        TaskStatus.IN_PROGRESS: "🔄",
                        TaskStatus.COMPLETED: "✅",
                        TaskStatus.FAILED: "❌",
                        TaskStatus.SKIPPED: "⏭️"
                    }
                    
                    f.write(f"### {status_emoji[task.status]} {task.id}: {task.description}\n\n")
                    
                    # Write task details
                    f.write(f"- **Status:** {task.status.value}\n")
                    f.write(f"- **Created:** {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    
                    if task.started_at:
                        f.write(f"- **Started:** {task.started_at.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    
                    if task.completed_at:
                        f.write(f"- **Completed:** {task.completed_at.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    
                    if task.dependencies:
                        f.write(f"- **Dependencies:** {', '.join(task.dependencies)}\n")
                    
                    # Write task notes
                    if task.notes:
                        f.write("\n#### Notes\n\n")
                        for note in task.notes:
                            f.write(f"- **{note['timestamp']}:** {note['content']}\n")
                    
                    f.write("\n")
        except Exception as e:
            print(f"Error writing tasks to log: {e}")
    
    def get_tasks_as_dict(self) -> Dict[str, Any]:
        """Get all tasks as a dictionary.
        
        Returns:
            Dictionary with tasks
        """
        return {
            "status": "success",
            "tasks": {task_id: task.to_dict() for task_id, task in self.tasks.items()},
            "count": len(self.tasks),
            "completed": sum(1 for task in self.tasks.values() if task.status == TaskStatus.COMPLETED)
        }
    
    def all_tasks_completed(self) -> bool:
        """Check if all tasks are completed.
        
        Returns:
            True if all tasks are completed, False otherwise
        """
        return all(task.status == TaskStatus.COMPLETED or task.status == TaskStatus.SKIPPED 
                  for task in self.tasks.values())
    
    def get_task_by_id(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a task by ID.
        
        Args:
            task_id: ID of the task to get
            
        Returns:
            Task as dictionary or None if not found
        """
        if task_id in self.tasks:
            return self.tasks[task_id].to_dict()
        return None 
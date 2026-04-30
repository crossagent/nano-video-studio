import os
import json
from typing import Optional, List, Dict, Any
from fastmcp import FastMCP
from task_db import TaskDB
import run_task

mcp = FastMCP("Nano Video Studio")

def get_db_registry():
    db = TaskDB()
    configs = db.get_all_model_configs()
    registry = {}
    for c in configs:
        ch, mod = c['channel_id'], c['model_id']
        if ch not in registry: registry[ch] = {}
        registry[ch][mod] = {
            "type": c['task_type'],
            "required_fields": c['required_params']
        }
    return registry

def _validate(channel_id, model_id, task_type, params):
    reg = get_db_registry()
    if channel_id not in reg:
        return False, f"Invalid channel: {channel_id}. Available: {list(reg.keys())}"
    if model_id not in reg[channel_id]:
        return False, f"Invalid model: {model_id} for {channel_id}."
    config = reg[channel_id][model_id]
    if config["type"] != task_type:
        return False, f"Model {model_id} is for {config['type']}, not {task_type}."
    missing = [f for f in config["required_fields"] if f not in params]
    if missing:
        return False, f"Missing params: {missing}"
    return True, ""

@mcp.tool()
def list_available_models() -> str:
    """List all models and their requirements."""
    return json.dumps(get_db_registry(), indent=2)

@mcp.tool()
def list_tasks(channel_id: Optional[str] = None, status: Optional[str] = None) -> str:
    """List all generation tasks from the big table."""
    db = TaskDB()
    tasks = db.list_tasks(channel_id=channel_id, status=status)
    if not tasks: return "No tasks found."
    
    res = [f"{'ID':<5} {'Channel':<12} {'Model':<20} {'Status':<10} {'Prompt'[:30]}"]
    res.append("-" * 80)
    for t in tasks:
        prompt = t['prompt'][:30] + "..." if len(t['prompt']) > 30 else t['prompt']
        res.append(f"{t['id']:<5} {t['channel_id']:<12} {t['model_id']:<20} {t['status']:<10} {prompt}")
    return "\n".join(res)

@mcp.tool()
def submit_image_task(channel_id: str, model_id: str, project: str, stage: str, prompt: str, extra_params: Dict[str, Any]) -> str:
    """Submit an IMAGE task."""
    ok, err = _validate(channel_id, model_id, "image", extra_params)
    if not ok: return f"Error: {err}"
    
    db = TaskDB()
    tid = db.add_task(channel_id, model_id, project, stage, prompt, extra_params)
    return f"Image task {tid} submitted successfully."

@mcp.tool()
def submit_video_task(channel_id: str, model_id: str, project: str, stage: str, prompt: str, extra_params: Dict[str, Any]) -> str:
    """Submit a VIDEO task."""
    ok, err = _validate(channel_id, model_id, "video", extra_params)
    if not ok: return f"Error: {err}"
    
    db = TaskDB()
    tid = db.add_task(channel_id, model_id, project, stage, prompt, extra_params)
    return f"Video task {tid} submitted successfully."

@mcp.tool()
def approve_task(task_id: int) -> str:
    """Approve a task in the big table."""
    db = TaskDB()
    db.update_task(task_id, status='approved')
    return f"Task {task_id} approved."

@mcp.tool()
def execute_task(task_id: int) -> str:
    """Run an approved task from the big table."""
    try:
        success, msg = run_task.execute_task(task_id)
        return msg
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def get_task_details(task_id: int) -> str:
    """Get full details (including JSON params) of a task."""
    db = TaskDB()
    t = db.get_task(task_id)
    return json.dumps(t, indent=2, default=str) if t else "Task not found."

if __name__ == "__main__":
    mcp.run()

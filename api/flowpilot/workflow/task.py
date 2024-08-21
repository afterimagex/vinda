from dataclasses import dataclass


@dataclass
class TaskSchema:
    name: str = "Task"
    description: str = ""
    id: int = 0
    status: bool = False
    completed_at: str = None
    created_at: str = None
    updated_at: str = None
    user_id: int = 0
    project_id: int = 0
    assigned_to: list = []
    tags: list = []
    due_date: str = None
    reminder_time: str = None

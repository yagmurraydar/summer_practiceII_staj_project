from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Task Manager API", version="1.0.0")

# --- DATA MODELS ---
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False

class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: int

# --- IN-MEMORY DATABASE ---
# Simulated database using a Python list and an ID counter
tasks_db = []
current_id = 1

# --- API ENDPOINTS ---

@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    """Create a new task."""
    global current_id
    new_task = TaskResponse(id=current_id, **task.model_dump())
    tasks_db.append(new_task)
    current_id += 1
    return new_task

@app.get("/tasks", response_model=List[TaskResponse])
def get_all_tasks():
    """Retrieve all tasks."""
    return tasks_db

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int):
    """Retrieve a single task by its ID."""
    for task in tasks_db:
        if task.id == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")

@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, updated_task: TaskCreate):
    """Update an existing task."""
    for index, task in enumerate(tasks_db):
        if task.id == task_id:
            new_task = TaskResponse(id=task_id, **updated_task.model_dump())
            tasks_db[index] = new_task
            return new_task
    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    """Delete a task from the list."""
    for index, task in enumerate(tasks_db):
        if task.id == task_id:
            tasks_db.pop(index)
            return
    raise HTTPException(status_code=404, detail="Task not found")

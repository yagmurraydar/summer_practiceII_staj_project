from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
import os

# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# --------------------------------------------------
# DATABASE MODEL
# --------------------------------------------------

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False)


# Create table
Base.metadata.create_all(bind=engine)


# --------------------------------------------------
# FASTAPI
# --------------------------------------------------

app = FastAPI(
    title="Task Manager API",
    version="1.0.0"
)


# --------------------------------------------------
# PYDANTIC MODELS
# --------------------------------------------------

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False


class TaskCreate(TaskBase):
    pass


class TaskResponse(TaskBase):
    id: int

    class Config:
        from_attributes = True


# --------------------------------------------------
# CREATE TASK
# --------------------------------------------------

@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED
)
def create_task(task: TaskCreate):

    db = SessionLocal()

    try:
        new_task = Task(
            title=task.title,
            description=task.description,
            completed=task.completed
        )

        db.add(new_task)
        db.commit()
        db.refresh(new_task)

        return new_task

    finally:
        db.close()


# --------------------------------------------------
# GET ALL TASKS
# --------------------------------------------------

@app.get(
    "/tasks",
    response_model=List[TaskResponse]
)
def get_all_tasks():

    db = SessionLocal()

    try:
        tasks = db.query(Task).all()
        return tasks

    finally:
        db.close()


# --------------------------------------------------
# GET SINGLE TASK
# --------------------------------------------------

@app.get(
    "/tasks/{task_id}",
    response_model=TaskResponse
)
def get_task(task_id: int):

    db = SessionLocal()

    try:
        task = db.query(Task).filter(
            Task.id == task_id
        ).first()

        if task is None:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )

        return task

    finally:
        db.close()


# --------------------------------------------------
# UPDATE TASK
# --------------------------------------------------

@app.put(
    "/tasks/{task_id}",
    response_model=TaskResponse
)
def update_task(
    task_id: int,
    updated_task: TaskCreate
):

    db = SessionLocal()

    try:
        task = db.query(Task).filter(
            Task.id == task_id
        ).first()

        if task is None:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )

        task.title = updated_task.title
        task.description = updated_task.description
        task.completed = updated_task.completed

        db.commit()
        db.refresh(task)

        return task

    finally:
        db.close()


# --------------------------------------------------
# DELETE TASK
# --------------------------------------------------

@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_task(task_id: int):

    db = SessionLocal()

    try:
        task = db.query(Task).filter(
            Task.id == task_id
        ).first()

        if task is None:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )

        db.delete(task)
        db.commit()

    finally:
        db.close()
# Kubernetes rolling update v2

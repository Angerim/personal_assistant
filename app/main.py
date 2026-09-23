from datetime import datetime, date, time

from fastapi import Depends, FastAPI
from sqlalchemy import select
from sqlalchemy.orm import Session
from .assistant import build_morning_briefing
from . import models
from .database import Base, engine, get_db
from .schemas import TaskCreate, TaskUpdate, TaskResponse


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Personal Assistant",
    description="My local AI personal assistant",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "Personal Assistant is alive."
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.post("/tasks", response_model=TaskResponse)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
):
    new_task = models.Task(
        title=task.title,
        scheduled_at=task.scheduled_at,
        notes=task.notes,
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


@app.get("/tasks", response_model=list[TaskResponse])
def get_tasks(
    db: Session = Depends(get_db),
):
    result = db.execute(
        select(models.Task).order_by(models.Task.scheduled_at)
    )

    return result.scalars().all()


@app.get("/tasks/today", response_model=list[TaskResponse])
def get_today_tasks(
    db: Session = Depends(get_db),
):
    today = date.today()

    start = datetime.combine(today, time.min)
    end = datetime.combine(today, time.max)

    result = db.execute(
        select(models.Task)
        .where(
            models.Task.scheduled_at >= start,
            models.Task.scheduled_at <= end,
        )
        .order_by(models.Task.scheduled_at)
    )

    return result.scalars().all()


@app.get("/morning")
def morning_briefing(
    db: Session = Depends(get_db),
):
    return {
        "message": build_morning_briefing(db)
    }

@app.patch("/tasks/{task_id}/complete", response_model=TaskResponse)
def complete_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    task = db.get(models.Task, task_id)

    if task is None:
        return {"error": "Task not found"}

    task.completed = True

    db.commit()
    db.refresh(task)

    return task

@app.patch("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task: TaskUpdate,
    db: Session = Depends(get_db),
):
    existing_task = db.get(models.Task, task_id)

    if existing_task is None:
        return {"error": "Task not found"}

    if task.title is not None:
        existing_task.title = task.title

    if task.scheduled_at is not None:
        existing_task.scheduled_at = task.scheduled_at

    if task.notes is not None:
        existing_task.notes = task.notes

    db.commit()
    db.refresh(existing_task)

    return existing_task

@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    task = db.get(models.Task, task_id)

    if task is None:
        return {"error": "Task not found"}

    db.delete(task)
    db.commit()

    return {
        "message": "Task deleted",
        "id": task_id,
    }
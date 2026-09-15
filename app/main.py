from datetime import datetime, date, time

from fastapi import Depends, FastAPI
from sqlalchemy import select
from sqlalchemy.orm import Session
from .assistant import build_morning_briefing
from . import models
from .database import Base, engine, get_db
from .schemas import TaskCreate, TaskResponse


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
from datetime import datetime

from pydantic import BaseModel


class TaskCreate(BaseModel):
    title: str
    scheduled_at: datetime | None = None
    notes: str | None = None


class TaskResponse(BaseModel):
    id: int
    title: str
    scheduled_at: datetime | None
    notes: str | None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
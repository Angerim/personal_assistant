from datetime import date, datetime, time

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Task


def get_today_tasks(db: Session) -> list[Task]:
    today = date.today()

    start = datetime.combine(today, time.min)
    end = datetime.combine(today, time.max)

    result = db.execute(
        select(Task)
        .where(
            Task.scheduled_at >= start,
            Task.scheduled_at <= end,
            Task.completed.is_(False),
        )
        .order_by(Task.scheduled_at)
    )

    return list(result.scalars().all())


def build_morning_briefing(db: Session) -> str:
    tasks = get_today_tasks(db)

    today = date.today().strftime("%d.%m.%Y")

    if not tasks:
        return (
            f"Доброе утро. Сегодня {today}.\n\n"
            "На сегодня ничего не запланировано."
        )

    lines = [
        f"Доброе утро. Сегодня {today}.",
        "",
        "План на сегодня:",
    ]

    for task in tasks:
        if task.scheduled_at:
            task_time = task.scheduled_at.strftime("%H:%M")
            line = f"• {task_time} — {task.title}"
        else:
            line = f"• {task.title}"

        if task.notes:
            line += f" ({task.notes})"

        lines.append(line)

    return "\n".join(lines)
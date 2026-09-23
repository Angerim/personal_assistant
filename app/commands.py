"""Small, predictable command parser for the first local assistant version."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta


CREATE_PREFIXES = ("добавь", "запланируй")
MORNING_PHRASES = ("утречко", "доброе утро", "утро")
TODAY_PHRASES = (
    "что у меня сегодня",
    "покажи сегодня",
    "план на сегодня",
    "дела на сегодня",
)


@dataclass
class ParsedTask:
    title: str
    scheduled_at: datetime | None
    notes: str | None


def normalize(text: str) -> str:
    return " ".join(text.strip().casefold().split()).strip("!?.,")


def command_type(text: str) -> str | None:
    normalized = normalize(text)

    if normalized in MORNING_PHRASES:
        return "morning"
    if normalized in TODAY_PHRASES:
        return "today"
    if normalized.startswith(CREATE_PREFIXES):
        return "create_task"

    return None


def parse_task_command(text: str, *, today: date | None = None) -> ParsedTask:
    """Parse a compact Russian task command without sending any data to an AI."""
    current_date = today or date.today()
    original = " ".join(text.strip().split())
    remainder = re.sub(
        r"^(?:добавь(?: дело)?|запланируй)\s+",
        "",
        original,
        count=1,
        flags=re.IGNORECASE,
    )

    notes = None
    note_match = re.search(r"\s+(?:заметка|не забудь)\s*[:—-]?\s*(.+)$", remainder, re.IGNORECASE)
    if note_match:
        notes = note_match.group(1).strip()
        remainder = remainder[: note_match.start()].strip(" ,—-")

    scheduled_date: date | None = None
    if re.search(r"\bзавтра\b", remainder, re.IGNORECASE):
        scheduled_date = current_date + timedelta(days=1)
        remainder = re.sub(r"\bзавтра\b", "", remainder, flags=re.IGNORECASE)
    elif re.search(r"\bсегодня\b", remainder, re.IGNORECASE):
        scheduled_date = current_date
        remainder = re.sub(r"\bсегодня\b", "", remainder, flags=re.IGNORECASE)
    else:
        date_match = re.search(r"\b(\d{1,2})[.](\d{1,2})(?:[.](\d{4}))?\b", remainder)
        if date_match:
            day, month, year = date_match.groups()
            scheduled_date = date(int(year) if year else current_date.year, int(month), int(day))
            remainder = remainder[: date_match.start()] + remainder[date_match.end() :]

    scheduled_time: time | None = None
    time_match = re.search(r"(?:\bв\s*)?(\d{1,2}):(\d{2})\b", remainder, re.IGNORECASE)
    if time_match:
        hour, minute = time_match.groups()
        scheduled_time = time(int(hour), int(minute))
        remainder = remainder[: time_match.start()] + remainder[time_match.end() :]

    remainder = re.sub(r"\b(?:в|на)\b", "", remainder, flags=re.IGNORECASE)
    title = re.sub(r"\s+", " ", remainder).strip(" ,—-")
    if not title:
        raise ValueError("Не вижу самого дела. Например: «добавь завтра в 19:00 тренировку».")

    scheduled_at = None
    if scheduled_date:
        scheduled_at = datetime.combine(scheduled_date, scheduled_time or time.min)

    return ParsedTask(title=title, scheduled_at=scheduled_at, notes=notes)

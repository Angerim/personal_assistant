from datetime import date, datetime
import unittest

from app.commands import command_type, parse_task_command


class CommandParserTests(unittest.TestCase):
    def test_recognizes_morning_and_today_commands(self):
        self.assertEqual(command_type("Утречко"), "morning")
        self.assertEqual(command_type("что у меня сегодня?"), "today")

    def test_parses_tomorrow_time_and_note(self):
        task = parse_task_command(
            "добавь завтра в 19:00 тренировку заметка: взять воду",
            today=date(2026, 9, 23),
        )

        self.assertEqual(task.title, "тренировку")
        self.assertEqual(task.scheduled_at, datetime(2026, 9, 24, 19, 0))
        self.assertEqual(task.notes, "взять воду")

    def test_parses_a_numeric_date(self):
        task = parse_task_command("добавь 01.10 в 08:30 лекцию", today=date(2026, 9, 23))

        self.assertEqual(task.title, "лекцию")
        self.assertEqual(task.scheduled_at, datetime(2026, 10, 1, 8, 30))


if __name__ == "__main__":
    unittest.main()

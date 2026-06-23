import logging
from typing import Optional

logger = logging.getLogger("jarvis")

class GoogleCalendarMock:
    """Mock integration for Google Calendar."""

    @staticmethod
    def create_event(
        title: str,
        start_time: str,
        end_time: Optional[str] = None,
        location: Optional[str] = None,
        description: Optional[str] = None
    ) -> dict:
        """
        Simulates creating an event in Google Calendar.
        """
        print("\n" + "=" * 50)
        print("📅 [GOOGLE CALENDAR] INTEGRATION - CREATING EVENT")
        print(f"  Title:       {title}")
        print(f"  Start Time:  {start_time}")
        if end_time:
            print(f"  End Time:    {end_time}")
        if location:
            print(f"  Location:    {location}")
        if description:
            print(f"  Description: {description}")
        print("=" * 50 + "\n")
        
        logger.info(f"Mock Calendar: Created event '{title}' scheduled at {start_time}")
        return {
            "status": "success",
            "provider": "google_calendar",
            "event_id": f"mock_evt_{hash(title) % 10000}",
            "title": title,
            "start_time": start_time
        }


class GoogleTasksMock:
    """Mock integration for Google Tasks."""

    @staticmethod
    def create_task(
        title: str,
        due: Optional[str] = None,
        notes: Optional[str] = None,
        priority: str = "medium"
    ) -> dict:
        """
        Simulates creating a task in Google Tasks.
        """
        print("\n" + "=" * 50)
        print("📋 [GOOGLE TASKS] INTEGRATION - CREATING TASK")
        print(f"  Title:       {title}")
        if due:
            print(f"  Due Date:    {due}")
        if notes:
            print(f"  Notes:       {notes}")
        print(f"  Priority:    {priority.upper()}")
        print("=" * 50 + "\n")
        
        logger.info(f"Mock Tasks: Created task '{title}' with due date {due}")
        return {
            "status": "success",
            "provider": "google_tasks",
            "task_id": f"mock_tsk_{hash(title) % 10000}",
            "title": title,
            "due": due,
            "priority": priority
        }

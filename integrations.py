import os
import os.path
import logging
from typing import Optional
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

logger = logging.getLogger("jarvis")

# Jeśli modyfikujesz te zakresy, usuń plik token.json.
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/tasks'
]

def get_google_credentials():
    """Obsługuje przepływ autoryzacji OAuth2 i zapisuje token.json."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                logger.error("Brak pliku credentials.json. Pobierz go z Google Cloud Console.")
                raise FileNotFoundError("Brak pliku credentials.json.")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            
    return creds

class GoogleCalendar:
    """Integracja z Google Calendar poprzez API."""

    @staticmethod
    def create_event(
        title: str,
        start_time: str,
        end_time: Optional[str] = None,
        location: Optional[str] = None,
        description: Optional[str] = None
    ) -> dict:
        try:
            creds = get_google_credentials()
            service = build('calendar', 'v3', credentials=creds)

            # Formatowanie i weryfikacja dat
            try:
                # Zignoruj normalizację jeśli to tylko data (całodniowe)
                if len(start_time) > 10:
                    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    start_time = start_dt.isoformat()
            except ValueError:
                pass
            
            # Sprawdź czy to wydarzenie całodniowe (tylko data YYYY-MM-DD bez godziny)
            is_all_day = len(start_time) <= 10 and 'T' not in start_time

            # Jeśli end_time nie jest podany
            if not end_time:
                try:
                    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    # Dodaj 1 godzinę tylko jeśli to nie jest samo YYYY-MM-DD
                    if len(start_time) > 10:
                        end_time = (start_dt + timedelta(hours=1)).isoformat()
                    else:
                        end_time = start_time
                except ValueError:
                    end_time = start_time
            else:
                try:
                    if len(end_time) > 10:
                        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                        end_time = end_dt.isoformat()
                except ValueError:
                    pass

            event = {
                'summary': title
            }
            
            if is_all_day:
                # Dla wydarzeń całodniowych Google wymaga klucza 'date', a nie 'dateTime'
                # Format to samo YYYY-MM-DD
                event['start'] = {'date': start_time[:10]}
                
                # Upewnijmy się że end_time też ma tylko 10 znaków
                end_date_str = end_time[:10] if end_time else start_time[:10]
                
                # Google wymaga żeby data końcowa była +1 dzień, ale API przyjmuje też równe daty
                event['end'] = {'date': end_date_str}
            else:
                event['start'] = {
                    'dateTime': start_time,
                    'timeZone': 'Europe/Warsaw',
                }
                event['end'] = {
                    'dateTime': end_time,
                    'timeZone': 'Europe/Warsaw',
                }
            
            if location:
                event['location'] = location
            if description:
                event['description'] = description

            logger.info(f"Wysyłam zapytanie do Google Calendar: {title}")
            event_result = service.events().insert(calendarId='primary', body=event).execute()
            
            logger.info(f"Kalendarz: Utworzono wydarzenie '{title}' -> {event_result.get('htmlLink')}")
            return {
                "status": "success",
                "provider": "google_calendar",
                "event_id": event_result.get('id'),
                "link": event_result.get('htmlLink'),
                "title": title,
                "start_time": start_time
            }
        except Exception as e:
            logger.error(f"Błąd podczas tworzenia wydarzenia w Google Calendar: {str(e)}")
            return {
                "status": "error",
                "provider": "google_calendar",
                "error": str(e)
            }


class GoogleTasks:
    """Integracja z Google Tasks poprzez API."""

    @staticmethod
    def create_task(
        title: str,
        due: Optional[str] = None,
        notes: Optional[str] = None,
        priority: int = 0
    ) -> dict:
        try:
            creds = get_google_credentials()
            service = build('tasks', 'v1', credentials=creds)

            task_body = {
                'title': title
            }
            
            # Google Tasks 'due' wymaga formatu RFC 3339: YYYY-MM-DDTHH:MM:SS.000Z
            if due:
                task_body['due'] = due if due.endswith('Z') else due + 'Z'
                
            if notes:
                task_body['notes'] = notes

            # Tasks API nie wspiera natywnego priorytetu, oznaczmy go wizualnie
            if priority == 1:
                task_body['title'] = f"❗ {title}"

            logger.info(f"Wysyłam zapytanie do Google Tasks: {title}")
            task_result = service.tasks().insert(tasklist='@default', body=task_body).execute()
            
            logger.info(f"Zadania: Utworzono zadanie '{title}' -> {task_result.get('id')}")
            return {
                "status": "success",
                "provider": "google_tasks",
                "task_id": task_result.get('id'),
                "title": title,
                "due": due,
            }
        except Exception as e:
            logger.error(f"Błąd podczas tworzenia zadania w Google Tasks: {str(e)}")
            return {
                "status": "error",
                "provider": "google_tasks",
                "error": str(e)
            }

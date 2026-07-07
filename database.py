import os
import datetime
from typing import Optional
from peewee import *

DB_NAME = os.getenv("DATABASE_PATH", "jarvis_memory.db")

db = SqliteDatabase(DB_NAME)

class BaseModel(Model):
    class Meta:
        database = db

class Task(BaseModel):
    id = AutoField()
    content = TextField()
    created_at = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
    is_done = IntegerField(default=0)
    priority = IntegerField(default=0)
    category = TextField(null=True)
    completed_at = DateTimeField(null=True)
    due_date = TextField(null=True) # Added for jarvis

    class Meta:
        table_name = 'tasks'

class Idea(BaseModel):
    id = AutoField()
    content = TextField()
    created_at = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
    category = TextField(null=True)

    class Meta:
        table_name = 'ideas'

class Reminder(BaseModel):
    id = AutoField()
    content = TextField()
    remind_at = DateTimeField()
    created_at = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
    is_sent = IntegerField(default=0)

    class Meta:
        table_name = 'reminders'

class RecurringReminder(BaseModel):
    id = AutoField()
    content = TextField()
    schedule_type = TextField()
    schedule_days = TextField(null=True)
    schedule_time = TextField()
    next_run = DateTimeField()
    created_at = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
    is_active = IntegerField(default=1)

    class Meta:
        table_name = 'recurring_reminders'


def init_db():
    """Inicjalizuje bazę danych i tworzy tabele, jeśli nie istnieją."""
    db.connect(reuse_if_open=True)
    db.create_tables([Task, Idea, Reminder, RecurringReminder])
    try:
        db.execute_sql('ALTER TABLE tasks ADD COLUMN completed_at TIMESTAMP')
    except Exception:
        pass
    try:
        db.execute_sql('ALTER TABLE tasks ADD COLUMN due_date TEXT')
    except Exception:
        pass
    db.close()

def _clean_row(row_dict):
    """Konwertuje obiekty datetime na napisy ISO."""
    if not row_dict:
        return row_dict
    for k, v in row_dict.items():
        if isinstance(v, datetime.datetime):
            row_dict[k] = v.isoformat()
    return row_dict

def _clean_rows(rows_list):
    return [_clean_row(r) for r in rows_list]

def add_task(content, priority=0, category=None, due_date=None):
    with db.connection_context():
        task = Task.create(content=content, priority=priority, category=category, due_date=due_date)
        return task.id

def add_idea(content, category=None):
    with db.connection_context():
        idea = Idea.create(content=content, category=category)
        return idea.id

def get_active_tasks(category=None):
    with db.connection_context():
        query = Task.select().where(Task.is_done == 0)
        if category:
            query = query.where(Task.category == category)
        return _clean_rows(list(query.order_by(Task.priority.desc(), Task.created_at.desc(), Task.id.desc()).dicts()))

def get_ideas(category=None):
    with db.connection_context():
        query = Idea.select()
        if category:
            query = query.where(Idea.category == category)
        return _clean_rows(list(query.order_by(Idea.created_at.desc(), Idea.id.desc()).dicts()))

if __name__ == "__main__":
    init_db()
    print("Baza danych zainicjowana.")

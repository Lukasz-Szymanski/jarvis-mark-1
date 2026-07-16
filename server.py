import logging
import sys
from dotenv import load_dotenv

# Load environment variables from .env file before importing agent, forcing override
load_dotenv(override=True)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent import JarvisAgent
from integrations import GoogleCalendar, GoogleTasks
from database import init_db, add_task, add_idea

# Initialize local database
init_db()

# =====================================================================
# SYSTEM LOGGING CONFIGURATION
# =====================================================================

# Setup structured logging to output cleanly to console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(name)s) %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("jarvis")

# =====================================================================
# FASTAPI APP INITIALIZATION & CORS MIDDLEWARE
# =====================================================================

app = FastAPI(
    title="J.A.R.V.I.S. Mark I - Core Server",
    description="Backend API for personal assistant parsing user commands into tasks and events.",
    version="1.0.0"
)

# Enable CORS for frontend communication (like Streamlit)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Jarvis Agent
try:
    agent = JarvisAgent()
except Exception as init_err:
    logger.critical(f"Failed to initialize Jarvis Agent on startup: {str(init_err)}")
    agent = None

# =====================================================================
# API ENDPOINTS & SCHEMAS
# =====================================================================

class ProcessRequest(BaseModel):
    command: str

@app.post("/process")
def process_command(payload: ProcessRequest):
    """
    Main endpoint that processes chaotic user prompts.
    It passes the input to JarvisAgent, determines the model dynamically,
    extracts Tasks and Events, triggers mock integrations, and logs everything.
    """
    if not agent:
        logger.error("JarvisAgent is uninitialized or failed during startup.")
        raise HTTPException(
            status_code=500,
            detail="AI Agent is not properly initialized. Check environment variables (.env)."
        )

    user_command = payload.command.strip()
    if not user_command:
        raise HTTPException(status_code=400, detail="Command cannot be empty.")

    logger.info(f"Received processing request: '{user_command[:100]}...'")

    try:
        # Run the agent pipeline
        result = agent.process_command(user_command)
        
        # Log routing details in a clear visual format in console
        routing_info = result["routing"]
        gatekeeper_info = result["gatekeeper"]
        
        print("\n" + "🚀" * 30)
        print("🤖 [J.A.R.V.I.S. DYNAMIC ROUTING DECISION]")
        print(f"  Gatekeeper Decision:  {'COMPLEX (Needs Advanced AI)' if gatekeeper_info['is_complex'] else 'SIMPLE (Fast Processing)'}")
        print(f"  Reasoning:            {gatekeeper_info['reasoning']}")
        print(f"  Provider Used:        {routing_info['provider'].upper()}")
        print(f"  Model Selected:       {routing_info['model_used']} ({routing_info['tier'].upper()} tier)")
        print("🚀" * 30 + "\n")
        
        logger.info(
            f"Command processed successfully using model '{routing_info['model_used']}' "
            f"({routing_info['tier']} tier)."
        )

        data = result["data"]
        
        # Trigger integrations automatically
        print("🔌 Triggering API Integrations for identified entities...")
        
        integrated_events = []
        integrated_tasks = []
        
        for event in data.get("events", []):
            event_res = GoogleCalendar.create_event(
                title=event["title"],
                start_time=event["start_time"],
                end_time=event.get("end_time"),
                location=event.get("location"),
                description=event.get("description")
            )
            integrated_events.append(event_res)
            
        for task in data.get("tasks", []):
            task_res = GoogleTasks.create_task(
                title=task["title"],
                due=task.get("due_date"),
                notes=task.get("description"),
                priority=task.get("priority", 0)
            )
            integrated_tasks.append(task_res)
            
            # Save task to local database
            add_task(
                content=f"{task['title']} - {task.get('description', '')}".strip(),
                priority=task.get("priority", 0),
                category=task.get("category"),
                due_date=task.get("due_date")
            )
            
        for idea in data.get("ideas", []):
            # Save idea to local database
            add_idea(
                content=idea["content"],
                category=idea.get("category")
            )
            print(f"💡 [SQLITE] Zapisano pomysł: {idea['content']}")
            
        # Append integration statuses to response for frontend tracking
        result["integrations"] = {
            "calendar_events": integrated_events,
            "tasks": integrated_tasks,
            "saved_to_db": True
        }

        return result

    except Exception as e:
        logger.error(f"Internal error processing command: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during command execution: {str(e)}"
        )


@app.get("/health")
def health_check():
    """Service health state check."""
    return {
        "status": "healthy",
        "agent_configured": agent is not None,
        "provider": agent.provider if agent else None
    }

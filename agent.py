import os
import json
import logging
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

# Logger configuration
logger = logging.getLogger("jarvis")

# =====================================================================
# PYDANTIC SCHEMAS FOR STRUCTURED OUTPUTS
# =====================================================================

class GatekeeperResult(BaseModel):
    """Result from the initial Gatekeeper check."""
    is_complex: bool = Field(
        description="True if the request involves scheduling conflicts, multiple steps, complex planning, or dates interpretation. False if it is a simple, direct command."
    )
    reasoning: str = Field(
        description="Brief explanation of why the request is classified as complex or simple."
    )


class TaskItem(BaseModel):
    """Represents a To-Do list item."""
    title: str = Field(description="Clear title of the task in Polish.")
    due_date: Optional[str] = Field(
        default=None, 
        description="Due date in YYYY-MM-DD format if specified or implied. Otherwise null."
    )
    priority: str = Field(
        default="medium", 
        description="Task priority: 'high', 'medium', or 'low'."
    )
    description: Optional[str] = Field(
        default=None, 
        description="Any extra details, context, or notes related to the task in Polish."
    )


class EventItem(BaseModel):
    """Represents a Calendar Event."""
    title: str = Field(description="Clear title of the calendar event in Polish.")
    start_time: str = Field(
        description="Event start date and time in YYYY-MM-DD HH:MM format. Must be resolved relative to system time."
    )
    end_time: Optional[str] = Field(
        default=None, 
        description="Event end date and time in YYYY-MM-DD HH:MM format if specified. Otherwise null."
    )
    location: Optional[str] = Field(
        default=None, 
        description="Location of the event if specified. Otherwise null."
    )
    description: Optional[str] = Field(
        default=None, 
        description="Any extra details, context, or notes related to the event in Polish."
    )


class ProcessedResult(BaseModel):
    """Final output containing parsed tasks and events, plus a friendly summary."""
    tasks: List[TaskItem] = Field(default_factory=list, description="List of parsed tasks.")
    events: List[EventItem] = Field(default_factory=list, description="List of parsed calendar events.")
    summary: str = Field(
        description="A friendly, professional summary in Polish describing the schedule, tasks, and recommendations."
    )


# =====================================================================
# AGENT CLASS WITH DYNAMIC MODEL ROUTING
# =====================================================================

class JarvisAgent:
    """
    Core AI logic for J.A.R.V.I.S. Mark I.
    Handles gatekeeper check and dynamic model switching for advanced queries.
    """

    def __init__(self):
        # Configure providers from environment variables
        self.provider = os.getenv("AI_PROVIDER", "gemini").lower()
        
        # Model definitions (can be overriden via env)
        if self.provider == "openai":
            self.model_cheap = os.getenv("OPENAI_MODEL_CHEAP", "gpt-4o-mini")
            self.model_expensive = os.getenv("OPENAI_MODEL_EXPENSIVE", "gpt-4o")
            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY is not set in environment variables.")
        else:
            # Default to gemini
            self.provider = "gemini"
            self.model_cheap = os.getenv("GEMINI_MODEL_CHEAP", "gemini-1.5-flash")
            self.model_expensive = os.getenv("GEMINI_MODEL_EXPENSIVE", "gemini-1.5-pro")
            self.api_key = os.getenv("GEMINI_API_KEY")
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY is not set in environment variables.")
        
        logger.info(f"JarvisAgent initialized using provider: '{self.provider}'")
        logger.info(f"Configured models -> Cheap: '{self.model_cheap}', Expensive: '{self.model_expensive}'")

    def _get_current_time_string(self) -> str:
        """Returns current system time in format YYYY-MM-DD HH:MM."""
        return datetime.now().strftime("%Y-%m-%d %H:%M")

    def _call_openai_gatekeeper(self, user_prompt: str, current_time: str) -> GatekeeperResult:
        """Helper to invoke OpenAI for Gatekeeper logic."""
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key)
        
        system_prompt = (
            "You are the Gatekeeper of J.A.R.V.I.S. Mark I. Your task is to analyze user requests "
            "and determine if they require complex reasoning, resolving scheduling conflicts, or multi-step execution "
            "planning (is_complex = True), or if they are simple single-step additions/requests (is_complex = False).\n"
            f"Aktualny czas systemu: {current_time}."
        )
        
        logger.info(f"Sending request to OpenAI Gatekeeper using model '{self.model_cheap}'...")
        completion = client.beta.chat.completions.parse(
            model=self.model_cheap,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format=GatekeeperResult,
            temperature=0.0
        )
        return completion.choices[0].message.parsed

    def _call_gemini_gatekeeper(self, user_prompt: str, current_time: str) -> GatekeeperResult:
        """Helper to invoke Google Gemini for Gatekeeper logic using the google-genai SDK."""
        from google import genai
        from google.genai import types
        
        client = genai.Client(api_key=self.api_key)
        
        system_prompt = (
            "You are the Gatekeeper of J.A.R.V.I.S. Mark I. Your task is to analyze user requests "
            "and determine if they require complex reasoning, resolving scheduling conflicts, or multi-step execution "
            "planning (is_complex = True), or if they are simple single-step additions/requests (is_complex = False).\n"
            f"Aktualny czas systemu: {current_time}."
        )
        
        logger.info(f"Sending request to Gemini Gatekeeper using model '{self.model_cheap}'...")
        response = client.models.generate_content(
            model=self.model_cheap,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=GatekeeperResult,
                temperature=0.0
            )
        )
        
        data = json.loads(response.text)
        return GatekeeperResult(**data)

    def _call_openai_executor(self, user_prompt: str, current_time: str, model_to_use: str) -> ProcessedResult:
        """Helper to invoke OpenAI to parse tasks and events."""
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key)
        
        system_prompt = (
            "You are J.A.R.V.I.S. Mark I, an advanced AI personal assistant.\n"
            "Your task is to parse messy user commands into structured calendar events and To-Do tasks.\n"
            f"Aktualny czas systemu: {current_time}.\n"
            "Interpret relative dates/times (like 'tomorrow', 'next Monday', 'in 2 hours') relative to this system time.\n"
            "Ensure that:\n"
            "1. Tasks have a title, optional due_date (YYYY-MM-DD), priority ('high', 'medium', 'low'), and description.\n"
            "2. Events have a title, start_time (YYYY-MM-DD HH:MM), optional end_time, location, and description.\n"
            "3. Provide a friendly and concise Polish summary describing the schedule and tasks you've generated."
        )
        
        logger.info(f"Sending request to OpenAI Executor using model '{model_to_use}'...")
        completion = client.beta.chat.completions.parse(
            model=model_to_use,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format=ProcessedResult,
            temperature=0.1
        )
        return completion.choices[0].message.parsed

    def _call_gemini_executor(self, user_prompt: str, current_time: str, model_to_use: str) -> ProcessedResult:
        """Helper to invoke Google Gemini to parse tasks and events using the google-genai SDK."""
        from google import genai
        from google.genai import types
        
        client = genai.Client(api_key=self.api_key)
        
        system_prompt = (
            "You are J.A.R.V.I.S. Mark I, an advanced AI personal assistant.\n"
            "Your task is to parse messy user commands into structured calendar events and To-Do tasks.\n"
            f"Aktualny czas systemu: {current_time}.\n"
            "Interpret relative dates/times (like 'tomorrow', 'next Monday', 'in 2 hours') relative to this system time.\n"
            "Ensure that:\n"
            "1. Tasks have a title, optional due_date (YYYY-MM-DD), priority ('high', 'medium', 'low'), and description.\n"
            "2. Events have a title, start_time (YYYY-MM-DD HH:MM), optional end_time, location, and description.\n"
            "3. Provide a friendly and concise Polish summary describing the schedule and tasks you've generated."
        )
        
        logger.info(f"Sending request to Gemini Executor using model '{model_to_use}'...")
        response = client.models.generate_content(
            model=model_to_use,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=ProcessedResult,
                temperature=0.1
            )
        )
        
        data = json.loads(response.text)
        return ProcessedResult(**data)

    def process_command(self, user_prompt: str) -> dict:
        """
        Executes the main pipeline:
        1. Check via Gatekeeper if prompt is complex.
        2. Select model (cheap vs expensive).
        3. Parse prompt into calendar events & tasks.
        4. Return structured dictionary with execution metrics.
        """
        current_time = self._get_current_time_string()
        
        try:
            # 1. Gatekeeper step
            if self.provider == "openai":
                gatekeeper = self._call_openai_gatekeeper(user_prompt, current_time)
            else:
                gatekeeper = self._call_gemini_gatekeeper(user_prompt, current_time)
                
            is_complex = gatekeeper.is_complex
            reasoning = gatekeeper.reasoning
            
            logger.info(f"Gatekeeper classification -> is_complex: {is_complex}. Reasoning: {reasoning}")
            
            # 2. Dynamic switching logic
            if is_complex:
                chosen_model = self.model_expensive
                model_tier = "expensive"
            else:
                chosen_model = self.model_cheap
                model_tier = "cheap"
                
            logger.info(f"Routing to: {model_tier.upper()} model tier -> '{chosen_model}'")
            
            # 3. Execution step
            if self.provider == "openai":
                result = self._call_openai_executor(user_prompt, current_time, chosen_model)
            else:
                result = self._call_gemini_executor(user_prompt, current_time, chosen_model)
                
            # 4. Compile final data with metadata
            return {
                "status": "success",
                "gatekeeper": {
                    "is_complex": is_complex,
                    "reasoning": reasoning
                },
                "routing": {
                    "provider": self.provider,
                    "model_used": chosen_model,
                    "tier": model_tier
                },
                "system_time": current_time,
                "data": result.model_dump()
            }
            
        except Exception as e:
            logger.exception("Error occurred in JarvisAgent.process_command")
            raise RuntimeError(f"Failed to process command with JarvisAgent: {str(e)}") from e

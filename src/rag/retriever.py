import asyncio
from typing import Generator
from google.adk.runners import Runner, RunConfig
from google.adk.agents.run_config import StreamingMode
from google.adk.sessions import InMemorySessionService
from google.adk.telemetry import TelemetryConfig, ContentCapturingMode
from google.genai import types

from src.agents.agents import financial_rag_workflow

session_service = InMemorySessionService()

APP_NAME = "financial_rag_app"
USER_ID = "default_user"

def _setup_runner(session_id: str) -> Runner:
    """Initializes the session and creates a runner."""
    try:
        asyncio.run(session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=session_id))
    except Exception as e:
        if "already exists" not in str(e).lower():
            pass

    return Runner(
        agent=financial_rag_workflow, 
        app_name=APP_NAME, 
        session_service=session_service
    )

def _get_run_config(streaming: bool = False) -> RunConfig:
    """Returns the unified RunConfig for the agent."""
    telemetry_cfg = TelemetryConfig(capture_message_content=ContentCapturingMode.SPAN_AND_EVENT)
    
    if streaming:
        return RunConfig(telemetry=telemetry_cfg, streaming_mode=StreamingMode.SSE)
    return RunConfig(telemetry=telemetry_cfg)

def _extract_text_from_event(event) -> str:
    """Extracts text from an event, handling both content parts and message fields safely."""
    if hasattr(event, "content") and event.content:
        # Abaikan gema dari input user (Stream ADK memberikan event input pengguna di awal stream)
        if getattr(event.content, "role", "") == "user":
            return ""
            
        if getattr(event.content, "parts", None):
            text_parts = [part.text for part in event.content.parts if hasattr(part, 'text') and part.text]
            if text_parts:
                return "".join(text_parts)
                
    if hasattr(event, "message") and isinstance(event.message, str):
        return event.message
        
    return ""

def ask_financial_agent_sync(query: str, session_id: str = "default_session") -> str:
    """Routes queries to the appropriate agent synchronously."""
    runner = _setup_runner(session_id)
    content = types.Content(role='user', parts=[types.Part(text=query)])
    
    events = runner.run(
        user_id=USER_ID, 
        session_id=session_id, 
        new_message=content,
        run_config=_get_run_config(streaming=False)
    )
    
    final_text = "Maaf, tidak ada respon dari agen."
    
    for event in events:
        if event.is_final_response():
            extracted = _extract_text_from_event(event)
            if extracted:
                final_text = extracted
            else:
                final_text = "Maaf, format respon tidak sesuai."
            break
            
    return final_text


def ask_financial_agent_stream(query: str, session_id: str = "default_session") -> Generator[str, None, None]:
    """Yields response text chunks in real-time."""
    runner = _setup_runner(session_id)
    content = types.Content(role='user', parts=[types.Part(text=query)])
    
    events = runner.run(
        user_id=USER_ID, 
        session_id=session_id, 
        new_message=content,
        run_config=_get_run_config(streaming=True)
    )
    
    yielded_any = False
    
    for event in events:
        if event.partial:
            if not event.content or not event.content.parts:
                continue
                
            has_fc = any(getattr(part, 'function_call', None) for part in event.content.parts)
            if has_fc:
                continue
                
            chunk = _extract_text_from_event(event)
            if chunk:
                yielded_any = True
                yield chunk
                
        elif event.is_final_response() and not yielded_any:
            final_text = _extract_text_from_event(event)
            if final_text:
                yield final_text
                yielded_any = True


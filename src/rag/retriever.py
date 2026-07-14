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
    """Helper to initialize the session and create a runner."""
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

def ask_financial_agent_sync(query: str, session_id: str = "default_session") -> str:
    """Routes queries to the appropriate agent synchronously."""
    runner = _setup_runner(session_id)
    content = types.Content(role='user', parts=[types.Part(text=query)])
    
    telemetry_cfg = TelemetryConfig(capture_message_content=ContentCapturingMode.SPAN_AND_EVENT)
    run_cfg = RunConfig(telemetry=telemetry_cfg)
    
    events = runner.run(
        user_id=USER_ID, 
        session_id=session_id, 
        new_message=content,
        run_config=run_cfg
    )
    
    final_text = "Maaf, tidak ada respon dari agen."
    
    for event in events:
        if event.is_final_response():
            if event.content and event.content.parts:
                final_text = event.content.parts[0].text
            elif hasattr(event, "message") and event.message:
                final_text = event.message
            else:
                final_text = "Maaf, format respon tidak sesuai."
            
    return final_text


def ask_financial_agent_stream(query: str, session_id: str = "default_session") -> Generator[str, None, None]:
    """Yields response text chunks in real-time."""
    runner = _setup_runner(session_id)
    content = types.Content(role='user', parts=[types.Part(text=query)])
    
    telemetry_cfg = TelemetryConfig(capture_message_content=ContentCapturingMode.SPAN_AND_EVENT)
    run_cfg = RunConfig(
        telemetry=telemetry_cfg,
        streaming_mode=StreamingMode.SSE
    )
    
    events = runner.run(
        user_id=USER_ID, 
        session_id=session_id, 
        new_message=content,
        run_config=run_cfg
    )
    
    yielded_any = False
    
    for event in events:
        if event.partial:
            if event.content and event.content.parts:
                has_text = any(part.text is not None for part in event.content.parts)
                has_fc = any(part.function_call is not None for part in event.content.parts)
                if has_text and not has_fc:
                    chunk = "".join(part.text for part in event.content.parts if part.text is not None)
                    if chunk:
                        yielded_any = True
                        yield chunk
        elif event.is_final_response():
            if not yielded_any:
                final_text = ""
                if event.content and event.content.parts:
                    final_text = event.content.parts[0].text
                elif hasattr(event, "message") and event.message:
                    final_text = event.message
                
                if final_text:
                    yield final_text
                    yielded_any = True


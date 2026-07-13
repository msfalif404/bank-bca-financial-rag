from google.adk.runners import Runner, RunConfig
from google.adk.sessions import InMemorySessionService
from google.adk.telemetry import TelemetryConfig, ContentCapturingMode
from google.genai import types

from src.agents.agents import financial_rag_workflow

session_service = InMemorySessionService()

APP_NAME = "financial_rag_app"
USER_ID = "default_user"

def ask_financial_agent_sync(query: str, session_id: str = "default_session") -> str:
    """
    Main function to ask queries to the financial RAG system.
    Routes queries to the appropriate agent synchronously.
    """
    try:
        session_service.create_session_sync(app_name=APP_NAME, user_id=USER_ID, session_id=session_id)
    except Exception as e:
        if "already exists" not in str(e).lower():
            print(f"Warning: Could not create session '{session_id}': {e}")
        
    runner = Runner(
        agent=financial_rag_workflow, 
        app_name=APP_NAME, 
        session_service=session_service
    )
    
    content = types.Content(role='user', parts=[types.Part(text=query)])
    
    # Tambahkan konfigurasi Telemetry agar isi pesan direkam ke Phoenix
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
                final_text = "Maaf, format respon tidak sesuai atau terjadi kesalahan internal agen."
            
    return final_text

import os
import litellm
from litellm import completion, Cache
from google.adk import Agent, Workflow, Event
from google.adk.models.lite_llm import LiteLlm

litellm.success_callback = ["langsmith"]
litellm.failure_callback = ["langsmith"]

from src.tools.tools import search_financial_records, get_report_overview
from src.prompts.manager import prompt_manager

litellm.cache = Cache(type="local")
llm_model = LiteLlm(model="openai/gpt-4o-mini")

def intent_classifier_node(node_input: str) -> Event:
    """Classifies user intent and routes to the appropriate agent."""
    try:
        response = completion(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt_manager.intent_classifier_prompt},
                {"role": "user", "content": str(node_input)}
            ],
            temperature=0
        )
        route = response.choices[0].message.content.strip().upper()
    except Exception as e:
        print(f"Warning: Intent classification failed - {e}")
        route = "OFF_TOPIC"
        
    valid_routes = {"DATA_SEARCH", "INSIGHTS", "OFF_TOPIC"}
    if route not in valid_routes:
        route = "OFF_TOPIC"
        
    return Event(route=[route], message=node_input)

data_search_agent = Agent(
    name="data_search_agent",
    model=llm_model,
    instruction=prompt_manager.data_search_prompt,
    tools=[search_financial_records]
)

insights_agent = Agent(
    name="insights_agent",
    model=llm_model,
    instruction=prompt_manager.insights_prompt,
    tools=[get_report_overview]
)

off_topic_agent = Agent(
    name="off_topic_agent",
    model=llm_model,
    instruction="Anda adalah asisten khusus analisis laporan keuangan Bank BCA. Jawab dengan singkat dan sopan bahwa Anda tidak bisa menjawab pertanyaan tersebut karena di luar konteks laporan keuangan bank atau panduan sistem Anda.",
)

financial_rag_workflow = Workflow(
    name="financial_rag_workflow",
    edges=[
        ("START", intent_classifier_node),
        (intent_classifier_node, {
            "DATA_SEARCH": data_search_agent,
            "INSIGHTS": insights_agent,
            "OFF_TOPIC": off_topic_agent
        })
    ]
)

from google.adk import Agent, Workflow, Event
from google.adk.models.lite_llm import LiteLlm

from src.tools.tools import search_financial_records, get_report_overview
from src.prompts.manager import prompt_manager

llm_model = LiteLlm(model="openai/gpt-4o-mini")

import litellm
from litellm import completion, Cache

# Aktifkan In-Memory Caching secara global untuk LiteLLM
litellm.cache = Cache(type="local")
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
    except Exception:
        route = "DATA_SEARCH"
        
    if route not in ["DATA_SEARCH", "INSIGHTS"]:
        route = "DATA_SEARCH"
        
    # Teruskan input asli ke agen selanjutnya
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

financial_rag_workflow = Workflow(
    name="financial_rag_workflow",
    edges=[
        ("START", intent_classifier_node),
        (intent_classifier_node, {
            "DATA_SEARCH": data_search_agent,
            "INSIGHTS": insights_agent
        })
    ]
)

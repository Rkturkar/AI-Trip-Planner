"""
Hotel Agent

Responsible for:
- Searching the best hotels for the destination
"""

from langchain_core.messages import AIMessage

from Backend.state import TravelState, increment_llm_calls
from Backend.tools.tavily_tool import tavily_search


def hotel_agent(state: TravelState) -> dict:
    """
    Search for hotels at the selected destination.
    """

    destination = (
        state.get("destination")
        or state.get("user_query")
    )

    query = f"Best hotels to stay in {destination}"

    hotel_data = tavily_search(query)

    return {
        "hotel_results": hotel_data,
        "messages": [
            AIMessage(
                content="🏨 Hotel information collected."
            )
        ],
        "llm_calls": increment_llm_calls(state),
    }
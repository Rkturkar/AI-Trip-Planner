"""
Activity Agent

Responsible for:
- Finding tourist attractions
- Finding things to do
- Collecting sightseeing information
"""

from langchain_core.messages import AIMessage

from Backend.state import TravelState, increment_llm_calls
from Backend.tools.tavily_tool import tavily_search


def activity_agent(state: TravelState) -> dict:
    """
    Search for tourist attractions and activities
    for the selected destination.
    """

    destination = (
        state.get("destination")
        or state.get("user_query")
    )

    query = (
        f"Top things to do and tourist attractions in {destination}"
    )

    activity_data = tavily_search(
        query=query,
        max_results=5,
    )

    return {
        "activity_results": activity_data,
        "messages": [
            AIMessage(
                content="🗺️ Activity information collected."
            )
        ],
        "llm_calls": increment_llm_calls(state),
    }
"""
Shared LangGraph state for the AI Trip Planner.
"""

from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class TravelState(TypedDict):
    """
    Shared state passed between all LangGraph nodes.
    """

    # Conversation
    messages: Annotated[list[AnyMessage], add_messages]

    # User Input
    user_query: str
    start_location: str
    transport_mode: str

    # Parsed Information
    destination: str

    # Agent Outputs
    flight_result: str
    hotel_results: str
    activity_results: str

    itinerary: str
    budget_estimate: str

    # Transport Details
    transport_info: dict
    nearest_station: str

    # Statistics
    llm_calls: int


def increment_llm_calls(state: TravelState) -> int:
    """
    Increment the LLM call counter.

    Every LangGraph node that invokes the LLM
    should use this helper.
    """
    return state.get("llm_calls", 0) + 1
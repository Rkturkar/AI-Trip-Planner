"""
Flight Agent

Responsible for:
- Searching flight information when transport mode is 'flight'
- Skipping flight search for train and bus
"""

from langchain_core.messages import AIMessage

from Backend.state import TravelState, increment_llm_calls
from Backend.tools.flight_tool import search_flight


def flight_agent(state: TravelState) -> dict:
    """
    Search flight information only when the user
    selects Flight as the transport mode.
    """

    transport_mode = state.get("transport_mode", "flight")

    # --------------------------------------------------
    # Skip for Train / Bus
    # --------------------------------------------------

    if transport_mode != "flight":
        return {
            "flight_result": (
                f"Transport mode: {transport_mode}. "
                "No flight search needed."
            ),
            "messages": [
                AIMessage(
                    content="⏭️ Skipped flight search (Train/Bus mode)."
                )
            ],
            "llm_calls": increment_llm_calls(state),
        }

    # --------------------------------------------------
    # Flight Search
    # --------------------------------------------------

    flight_data = search_flight(
        state["user_query"]
    )

    return {
        "flight_result": flight_data,
        "messages": [
            AIMessage(
                content="✈️ Flight information collected."
            )
        ],
        "llm_calls": increment_llm_calls(state),
    }
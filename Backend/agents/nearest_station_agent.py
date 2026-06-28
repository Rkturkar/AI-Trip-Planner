"""
Nearest Boarding Point Agent

Responsible for finding the most suitable railway station,
bus stand, or airport based on the selected transport mode.
"""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from Backend.core.llm import llm
from Backend.state import TravelState, increment_llm_calls
from Backend.tools.tavily_tool import tavily_search


def nearest_station_agent(state: TravelState) -> dict: 
    """
    Find the nearest boarding point for the chosen transport mode.
    """

    mode = state.get("transport_mode", "flight")
    start = state.get("start_location", "")
    destination = state.get("destination", "")

    if not start:
        return {
            "nearest_station": "",
            "llm_calls": increment_llm_calls(state),
        }

    # ------------------------------------------------------
    # Search Query
    # ------------------------------------------------------

    if mode == "train":
        query = (
            f"nearest railway station to {start} "
            f"for trains to {destination}"
        )

    elif mode == "bus":
        query = (
            f"nearest bus stand or KSRTC MSRTC "
            f"bus terminus near {start} "
            f"for buses to {destination}"
        )

    else:
        query = (
            f"nearest airport to {start} "
            f"for flights to {destination}"
        )

    search_result = tavily_search(
        query=query,
        max_results=3,
    )

    # ------------------------------------------------------
    # LLM Prompt
    # ------------------------------------------------------

    prompt = f"""
The user is starting their journey from:

{start}

Transport mode:

{mode}

Destination:

{destination}

Based on the search results below,
identify the single best boarding point.

Also provide 2-3 practical travel tips.

Search Results:

{search_result}

Reply in 3-4 concise lines.
"""

    response = llm.invoke(
        [
            SystemMessage(
                content=(
                    "You are a local travel expert "
                    "who knows India's transport network."
                )
            ),
            HumanMessage(content=prompt),
        ]
    )

    return {
        "nearest_station": response.content,
        "messages": [
            AIMessage(
                content="📍 Nearest boarding point identified."
            )
        ],
        "llm_calls": increment_llm_calls(state),
    }
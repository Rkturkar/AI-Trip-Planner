"""
Query Planner Agent

Responsible for:
- Understanding the user's travel request
- Extracting the destination
- Building transport information
"""

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)

from Backend.core.llm import llm
from Backend.core.transport import build_transport_info 
from Backend.state import (
    TravelState,
    increment_llm_calls,
)


def query_planner(state: TravelState) -> dict:
    """
    Analyse the user's travel request and extract
    the destination and travel intent.
    """

    prompt = f"""
You are a travel intent parser.

Extract the following information:

1. Destination city/country
2. Travel dates (if mentioned)
3. Number of travellers (if mentioned)
4. Budget range (if mentioned)
5. Key interests (beaches, mountains, food, culture, adventure, etc.)

Return plain text only using labels.

User Query:
{state["user_query"]}

Starting Location:
{state.get("start_location", "Not specified")}

Transport Mode:
{state.get("transport_mode", "flight")}
"""

    response = llm.invoke(
        [
            SystemMessage(
                content="You extract structured travel information."
            ),
            HumanMessage(content=prompt),
        ]
    )

    destination_line = next(
        (
            line
            for line in response.content.splitlines()
            if "destination" in line.lower()
        ),
        "",
    )

    if ":" in destination_line:
        destination = destination_line.split(":", 1)[1].strip()
    else:
        destination = state["user_query"]

    transport_info = build_transport_info(
        start_location=state.get("start_location", ""),
        destination=destination,
        transport_mode=state.get("transport_mode", "flight"),
    )

    return {
        "destination": destination,

        "transport_info": transport_info,

        "messages": [
            AIMessage(
                content=f"Parsed destination: {destination}"
            )
        ],

        "llm_calls": increment_llm_calls(state),
    }
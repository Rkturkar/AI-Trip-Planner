"""
Itinerary Agent

Responsible for:
- Creating a detailed day-by-day itinerary
- Including transport information
- Using hotel and activity research
"""

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from Backend.core.llm import llm
from Backend.state import TravelState, increment_llm_calls


def itinerary_agent(state: TravelState) -> dict:
    """
    Generate a complete day-by-day itinerary.
    """

    mode = state.get("transport_mode", "flight")
    start = state.get("start_location", "your location")
    transport_info = state.get("transport_info", {})

    # --------------------------------------------------
    # Transport Section
    # --------------------------------------------------

    if mode in ("bus", "train"):

        transport_section = f"""
TRANSPORT

Starting From:
{start}

Destination:
{state["destination"]}

Mode:
{mode.upper()}

Nearest Boarding Point:
{state.get("nearest_station", "Not Available")}

Booking Link:
{transport_info.get("booking_url", "")}

Travel Tip:
{transport_info.get("boarding_tip", "")}
"""

    else:

        transport_section = f"""
FLIGHT DETAILS

Starting From:
{start}

Destination:
{state["destination"]}

Flight Information:
{state["flight_result"]}

Airport Tip:
{transport_info.get("boarding_tip", "")}
"""

    # --------------------------------------------------
    # Prompt
    # --------------------------------------------------

    prompt = f"""
Create a detailed day-by-day travel itinerary.

Destination:
{state["destination"]}

Starting From:
{start}

Transport Mode:
{mode.upper()}

Original User Request:
{state["user_query"]}

{transport_section}

Hotel Options:
{state["hotel_results"]}

Activities:
{state["activity_results"]}

Requirements:

1. Create a practical day-by-day itinerary.

2. Mention recommended places to visit.

3. Suggest local food experiences.

4. Include transportation tips.

5. Mention the best visiting time.

6. Keep the itinerary realistic.

7. Include travel time from {start} on Day 1.
"""

    response = llm.invoke(
        [
            SystemMessage(
                content=(
                    "You are an expert travel planner. "
                    "Create vivid, practical itineraries."
                )
            ),
            HumanMessage(content=prompt),
        ]
    )

    return {
        "itinerary": response.content,
        "messages": [response],
        "llm_calls": increment_llm_calls(state),
    }
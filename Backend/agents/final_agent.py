"""
Final Agent

Responsible for:
- Combining all agent outputs
- Creating the final travel plan
"""

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from Backend.core.llm import llm
from Backend.state import TravelState, increment_llm_calls


def final_agent(state: TravelState) -> dict:
    """
    Generate the final travel plan.
    """

    mode = state.get("transport_mode", "flight")
    transport_info = state.get("transport_info", {})
    start = state.get("start_location", "your city")

    # ------------------------------------------------------
    # Transport Section
    # ------------------------------------------------------

    if mode in ("bus", "train") and transport_info.get("booking_url"):

        transport_section = f"""
## 🎟️ Book Your {mode.capitalize()} Now

Starting From:
{start}

Destination:
{state["destination"]}

Booking Link:
{transport_info.get("booking_url")}

Booking Label:
{transport_info.get("booking_label")}

Nearest Boarding Point:
{state.get("nearest_station", "")}

Travel Tip:
{transport_info.get("boarding_tip", "")}
"""

    else:

        transport_section = f"""
## ✈️ Flight Information

{state.get("flight_result", "")}

Departure Tip:

{transport_info.get("boarding_tip", "")}
"""

    # ------------------------------------------------------
    # Prompt
    # ------------------------------------------------------

    prompt = f"""
You are a professional travel planner.

Create a complete travel plan using all available information.

==================================================

DESTINATION:
{state["destination"]}

STARTING LOCATION:
{start}

TRANSPORT MODE:
{mode.upper()}

USER REQUEST:
{state["user_query"]}

==================================================

TRANSPORT

{transport_section}

==================================================

HOTELS

{state["hotel_results"]}

==================================================

ACTIVITIES

{state["activity_results"]}

==================================================

ITINERARY

{state["itinerary"]}

==================================================

BUDGET

{state["budget_estimate"]}

==================================================

Create a professional travel plan with the following sections.

# Trip Overview

- Destination
- Starting Location
- Best Time to Visit

# Transportation

Explain how to reach the destination.

If transport mode is Bus or Train,

include the booking link prominently.

# Hotels

Recommend the best hotels.

# Day-by-Day Itinerary

Use the itinerary provided.

# Food & Local Experiences

Suggest famous foods and experiences.

# Budget Breakdown

Use the generated budget.

# Travel Tips

Provide practical advice.

Use Markdown formatting.

Use headings and bullet points.

Make the response attractive and easy to read.
"""

    response = llm.invoke(
        [
            SystemMessage(
                content=(
                    "You are a world-class travel planner. "
                    "Create comprehensive and inspiring travel plans."
                )
            ),
            HumanMessage(content=prompt),
        ]
    )

    return {
        "messages": [response],
        "llm_calls": increment_llm_calls(state),
    }
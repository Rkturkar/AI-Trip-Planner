"""
Budget Agent

Responsible for:
- Estimating the complete trip budget
- Providing a realistic cost breakdown
"""

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from Backend.core.llm import llm
from Backend.state import TravelState, increment_llm_calls


def budget_agent(state: TravelState) -> dict:
    """
    Estimate the overall travel budget.
    """

    mode = state.get("transport_mode", "flight")

    prompt = f"""
Based on this travel plan, provide a realistic budget estimate in
Indian Rupees (INR).

Destination:
{state["destination"]}

Starting From:
{state.get("start_location", "Not specified")}

Transport Mode:
{mode.upper()}

Original User Request:
{state["user_query"]}

Itinerary:
{state["itinerary"]}

Provide the following breakdown:

1. {mode.capitalize()} Fare (Round Trip Per Person)

2. Accommodation (Per Night)

3. Food & Dining (Per Day)

4. Activities & Sightseeing

5. Local Transport

6. Miscellaneous Expenses

7. Total Estimated Budget

Guidelines:

- Use realistic Indian prices.
- Keep the response concise.
- Format using bullet points.
"""

    response = llm.invoke(
        [
            SystemMessage(
                content=(
                    "You are a travel budget expert. "
                    "Provide realistic cost estimates."
                )
            ),
            HumanMessage(content=prompt),
        ]
    )

    return {
        "budget_estimate": response.content,
        "messages": [
            HumanMessage(
                content="💰 Budget estimate generated."
            )
        ],
        "llm_calls": increment_llm_calls(state),
    }
"""
Follow-up Chat Service

Handles follow-up questions about an already generated trip plan.
"""

from langchain_core.messages import HumanMessage, SystemMessage

from Backend.core.llm import llm


async def followup_chat(request):
    """
    Answer follow-up questions using the previously
    generated trip context.
    """

    context = f"""
You are an expert AI Travel Assistant.

The user already has the following travel plan.

Destination:
{request.destination}

Starting Location:
{request.start_location}

Transport Mode:
{request.transport_mode}

Original User Query:
{request.user_query}

Budget Estimate:
{request.budget_estimate or "Not Available"}

Flight Information:
{request.flight_result or "Not Available"}

Hotel Information:
{request.hotel_results or "Not Available"}

Itinerary:
{request.itinerary or "Not Available"}

Final Travel Plan:
{request.final_plan or "Not Available"}

------------------------------------------------------

Answer ONLY the user's follow-up question.

If the answer exists in the itinerary,
use that information.

Otherwise answer like a professional travel assistant.

User Question:

{request.user_message}

Keep your answer concise, helpful and accurate.
"""

    response = llm.invoke(
        [
            SystemMessage(
                content=(
                    "You are a professional AI Travel Assistant."
                )
            ),
            HumanMessage(content=context),
        ]
    )

    return {
        "reply": response.content
    }
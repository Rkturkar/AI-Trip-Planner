"""
Planner Service

Handles trip planning using the LangGraph workflow.
"""

import asyncio
import json
from typing import AsyncGenerator

from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage

from Backend.graph import app as graph_app
from Backend.schemas.trip import TripRequest, TripResponse
from Backend.state import TravelState


# --------------------------------------------------
# Build Initial State
# --------------------------------------------------

def create_initial_state(req: TripRequest) -> TravelState:
    """
    Create the initial LangGraph state.
    """

    return {

        "messages": [
            HumanMessage(content=req.query)
        ],

        "user_query": req.query,

        "start_location": req.start_location,

        "transport_mode": req.transport_mode,

        "destination": "",

        "flight_result": "",

        "hotel_results": "",

        "activity_results": "",

        "itinerary": "",

        "budget_estimate": "",

        "transport_info": {},

        "nearest_station": "",

        "llm_calls": 0,
    }


# --------------------------------------------------
# Generate Trip
# --------------------------------------------------

async def plane_trip(req: TripRequest) -> TripResponse:
    """
    Generate a complete trip plan.
    """

    if not req.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty.",
        )

    state = create_initial_state(req)

    try:

        result: TravelState = await asyncio.to_thread(
            graph_app.invoke,
            state,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

    final_plan = ""

    if result.get("messages"):
        final_plan = result["messages"][-1].content

    return TripResponse(

        destination=result.get("destination", ""),

        start_location=result.get(
            "start_location",
            req.start_location,
        ),

        transport_mode=result.get(
            "transport_mode",
            req.transport_mode,
        ),

        transport_info=result.get(
            "transport_info",
            {},
        ),

        nearest_station=result.get(
            "nearest_station",
            "",
        ),

        flight_result=result.get(
            "flight_result",
            "",
        ),

        hotel_results=result.get(
            "hotel_results",
            "",
        ),

        activity_results=result.get(
            "activity_results",
            "",
        ),

        itinerary=result.get(
            "itinerary",
            "",
        ),

        budget_estimate=result.get(
            "budget_estimate",
            "",
        ),

        final_plan=final_plan,

        llm_calls=result.get(
            "llm_calls",
            0,
        ),
    )


# --------------------------------------------------
# Streaming
# --------------------------------------------------

async def stream_trip(req: TripRequest):

    if not req.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty.",
        )

    state = create_initial_state(req)

    async def event_generator() -> AsyncGenerator[str, None]:

        steps = {

            "query_planner":
                "🔍 Analysing your query...",

            "nearest_station_agent":
                "📍 Finding nearest boarding point...",

            "flight_agent":
                "✈️ Searching flights...",

            "hotel_agent":
                "🏨 Finding hotels...",

            "activity_agent":
                "🗺️ Finding attractions...",

            "itinerary_agent":
                "📅 Building itinerary...",

            "budget_agent":
                "💰 Estimating budget...",

            "final_agent":
                "✨ Preparing your trip..."
        }

        try:

            for node_name, node_output in graph_app.stream(
                state,
                stream_mode="updates",
            ):

                payload = {

                    "step": node_name,

                    "label": steps.get(
                        node_name,
                        node_name,
                    ),

                    "data": "",
                }

                yield f"data: {json.dumps(payload)}\n\n"

                await asyncio.sleep(0)

            result = await asyncio.to_thread(
                graph_app.invoke,
                state,
            )

            final = ""

            if result.get("messages"):
                final = result["messages"][-1].content

            payload = {

                "step": "done",

                "label": "Trip Ready",

                "data": final,

                "destination":
                    result.get("destination", ""),

                "start_location":
                    result.get("start_location", ""),

                "transport_mode":
                    result.get("transport_mode", ""),

                "transport_info":
                    result.get("transport_info", {}),

                "nearest_station":
                    result.get("nearest_station", ""),

                "flight_result":
                    result.get("flight_result", ""),

                "hotel_results":
                    result.get("hotel_results", ""),

                "activity_results":
                    result.get("activity_results", ""),

                "itinerary":
                    result.get("itinerary", ""),

                "budget_estimate":
                    result.get("budget_estimate", ""),

                "llm_calls":
                    result.get("llm_calls", 0),
            }

            yield f"data: {json.dumps(payload)}\n\n"

        except Exception as exc:

            payload = {

                "step": "error",

                "label": "Something went wrong",

                "data": str(exc),
            }

            yield f"data: {json.dumps(payload)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )
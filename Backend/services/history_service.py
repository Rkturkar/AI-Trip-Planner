"""
History Service

Handles all trip history operations.
"""

from fastapi import HTTPException

from Backend.database.crud import (
    save_chat,
    get_all_chats,
    get_chat_by_id,
    delete_chat,
)


# --------------------------------------------------
# Save Trip
# --------------------------------------------------

def save_trip(request):
    """
    Save a completed trip.
    """

    row_id = save_chat(
    session_id=request.session_id,

    destination=request.destination,

    user_query=request.user_query,

    start_location=request.start_location,

    transport_mode=request.transport_mode,

    nearest_station=request.nearest_station,

    booking_url=request.booking_url,

    flight_result=request.flight_result,

    hotel_results=request.hotel_results,

    activity_results=request.activity_results,

    itinerary=request.itinerary,

    budget_estimate=request.budget_estimate,

    final_plan=request.final_plan,

    vibes=request.vibes,

    llm_calls=request.llm_calls,
)

    if row_id is None:
        raise HTTPException(
            status_code=500,
            detail="Failed to save trip.",
        )

    return {
        "success": True,
        "id": row_id,
    }


# --------------------------------------------------
# Get History
# --------------------------------------------------

def get_trip_history(session_id: str):
    """
    Return all trips of a session.
    """

    chats = get_all_chats(session_id)

    return {
        "chats": chats
    }


# --------------------------------------------------
# Get Single Trip
# --------------------------------------------------

def get_trip(chat_id: int, session_id: str):
    """
    Return one trip.
    """

    chat = get_chat_by_id(
        chat_id,
        session_id,
    )

    if chat is None:
        raise HTTPException(
            status_code=404,
            detail="Trip not found.",
        )

    return chat


# --------------------------------------------------
# Delete Trip
# --------------------------------------------------

def delete_trip(chat_id: int, session_id: str):
    """
    Delete a trip.
    """

    deleted = delete_chat(
        chat_id,
        session_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Trip not found.",
        )

    return {
        "success": True
    }
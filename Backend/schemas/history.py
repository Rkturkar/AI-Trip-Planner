from pydantic import BaseModel


class SaveChatRequest(BaseModel):
    session_id: str

    destination: str
    user_query: str

    start_location: str = ""
    transport_mode: str = "flight"

    nearest_station: str = ""
    booking_url: str = ""

    flight_result: str = ""
    hotel_results: str = ""
    activity_results: str = ""

    itinerary: str = ""
    budget_estimate: str = ""

    final_plan: str = ""

    vibes: str = ""

    llm_calls: int = 0
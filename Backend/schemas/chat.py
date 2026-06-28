from pydantic import BaseModel


class FollowUpRequest(BaseModel):
    user_message: str

    destination: str = ""
    user_query: str = ""

    itinerary: str = ""
    budget_estimate: str = ""
    final_plan: str = ""

    flight_result: str = ""
    hotel_results: str = ""

    start_location: str = ""
    transport_mode: str = "flight"
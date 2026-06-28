from pydantic import BaseModel


class TripRequest(BaseModel):
    query: str
    start_location: str = ""
    transport_mode: str = "flight"


class TripResponse(BaseModel):
    destination: str

    start_location: str
    transport_mode: str

    transport_info: dict
    nearest_station: str

    flight_result: str
    hotel_results: str
    activity_results: str

    itinerary: str
    budget_estimate: str

    final_plan: str

    llm_calls: int
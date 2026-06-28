import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("AVIATIONSTACK_API_KEY")

BASE_URL = "http://api.aviationstack.com/v1/flights"


def search_flight(query: str) -> str:
    """
    Search live flight information using AviationStack API.
    """

    if not API_KEY:
        return (
            "✈️ Flight search is unavailable "
            "(AVIATIONSTACK_API_KEY not configured)."
        )

    try:
        response = requests.get(
            BASE_URL,
            params={
                "access_key": API_KEY,
                "limit": 5,
            },
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

    except requests.Timeout:
        return "Flight search timed out."

    except requests.HTTPError as e:
        return f"HTTP Error: {e}"

    except requests.RequestException as e:
        return f"Flight search failed: {e}"

    except Exception as e:
        return str(e)

    flights = data.get("data", [])

    if not flights:
        return "No flight data found."

    result = []

    for flight in flights[:5]:

        airline = flight.get("airline", {}).get("name", "Unknown Airline")

        flight_no = flight.get("flight", {}).get("iata", "N/A")

        departure = flight.get("departure", {})
        arrival = flight.get("arrival", {})

        dep_airport = departure.get("airport", "Unknown Airport")
        dep_code = departure.get("iata", "")
        dep_time = departure.get("scheduled", "")

        arr_airport = arrival.get("airport", "Unknown Airport")
        arr_code = arrival.get("iata", "")
        arr_time = arrival.get("scheduled", "")

        status = flight.get("flight_status", "Unknown").capitalize()

        result.append(
            f"""
✈ Flight : {flight_no}
Airline : {airline}

Departure :
{dep_airport} ({dep_code})
{dep_time}

Arrival :
{arr_airport} ({arr_code})
{arr_time}

Status :
{status}
"""
        )

    return "\n".join(result)
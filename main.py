"""
AI Trip Planner
Entry Point
"""

from langchain_core.messages import HumanMessage

from Backend.graph import app


def run_cli():
    """
    Run the AI Trip Planner from the terminal.
    """

    print("=" * 60)
    print("🌍 AI Trip Planner")
    print("=" * 60)

    user_query = input("\nEnter your travel request:\n> ").strip()

    if not user_query:
        print("Query cannot be empty.")
        return

    start_location = input(
        "\nEnter your starting location:\n> "
    ).strip()

    print("\nChoose Transport Mode")
    print("1. Flight")
    print("2. Train")
    print("3. Bus")

    choice = input("\nChoice: ").strip()

    transport_map = {
        "1": "flight",
        "2": "train",
        "3": "bus",
    }

    transport_mode = transport_map.get(
        choice,
        "flight",
    )

    state = {

        "messages": [
            HumanMessage(content=user_query)
        ],

        "user_query": user_query,

        "start_location": start_location,

        "transport_mode": transport_mode,

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

    print("\nGenerating your trip...\n")

    result = app.invoke(state)

    print("=" * 60)
    print("FINAL TRAVEL PLAN")
    print("=" * 60)

    print(result["messages"][-1].content)

    print("\nLLM Calls :", result["llm_calls"])


if __name__ == "__main__":
    run_cli()
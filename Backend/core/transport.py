"""
Transport utility functions for the AI Trip Planner.
"""


def build_transport_info(
    start_location: str,
    destination: str,
    transport_mode: str,
) -> dict:
    """
    Build transport information and booking links
    based on the selected transport mode.
    """

    transport_info = {
        "mode": transport_mode,
        "from": start_location,
        "to": destination,
        "booking_url": "",
        "booking_label": "",
        "boarding_tip": "",
    }

    src = start_location.replace(" ", "%20")
    dest = destination.replace(" ", "%20")

    # --------------------------------------------------
    # Train
    # --------------------------------------------------

    if transport_mode == "train":

        transport_info["booking_url"] = (
            "https://www.irctc.co.in/nget/train-search"
            f"?fromStation={src}&toStation={dest}"
        )

        transport_info["booking_label"] = "Book Train on IRCTC →"

        transport_info["boarding_tip"] = (
            f"The nearest major railway station to "
            f"{start_location} will be your boarding point. "
            f"Reach the station at least 30–45 minutes before departure."
        )

    # --------------------------------------------------
    # Bus
    # --------------------------------------------------

    elif transport_mode == "bus":

        transport_info["booking_url"] = (
            f"https://www.redbus.in/bus-tickets/"
            f"{src}-to-{dest}"
        )

        transport_info["booking_label"] = "Book Bus on RedBus →"

        transport_info["boarding_tip"] = (
            f"Find the nearest bus stand in "
            f"{start_location}. Check your RedBus ticket "
            f"for the exact boarding point."
        )

    # --------------------------------------------------
    # Flight
    # --------------------------------------------------

    else:

        transport_info["booking_url"] = ""

        transport_info["booking_label"] = ""

        transport_info["boarding_tip"] = (
            f"The nearest airport to {start_location} "
            f"will be your departure point. "
            f"Arrive at least 2 hours before your flight."
        )

    return transport_info

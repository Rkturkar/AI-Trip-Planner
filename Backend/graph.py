"""
LangGraph workflow for the AI Trip Planner.
"""

from langgraph.graph import START, END, StateGraph

from Backend.state import TravelState

from Backend.agents.query_agent import query_planner
from Backend.agents.nearest_station_agent import nearest_station_agent
from Backend.agents.flight_agent import flight_agent
from Backend.agents.hotel_agent import hotel_agent
from Backend.agents.activity_agent import activity_agent
from Backend.agents.itinerary_agent import itinerary_agent
from Backend.agents.budget_agent import budget_agent
from Backend.agents.final_agent import final_agent


# ------------------------------------------------------
# Create Graph
# ------------------------------------------------------

graph = StateGraph(TravelState)


# ------------------------------------------------------
# Register Nodes
# ------------------------------------------------------

graph.add_node("query_planner", query_planner)

graph.add_node(
    "nearest_station_agent",
    nearest_station_agent,
)

graph.add_node(
    "flight_agent",
    flight_agent,
)

graph.add_node(
    "hotel_agent",
    hotel_agent,
)

graph.add_node(
    "activity_agent",
    activity_agent,
)

graph.add_node(
    "itinerary_agent",
    itinerary_agent,
)

graph.add_node(
    "budget_agent",
    budget_agent,
)

graph.add_node(
    "final_agent",
    final_agent,
)


# ------------------------------------------------------
# Register Edges
# ------------------------------------------------------

graph.add_edge(
    START,
    "query_planner",
)

graph.add_edge(
    "query_planner",
    "nearest_station_agent",
)

graph.add_edge(
    "nearest_station_agent",
    "flight_agent",
)

graph.add_edge(
    "flight_agent",
    "hotel_agent",
)

graph.add_edge(
    "hotel_agent",
    "activity_agent",
)

graph.add_edge(
    "activity_agent",
    "itinerary_agent",
)

graph.add_edge(
    "itinerary_agent",
    "budget_agent",
)

graph.add_edge(
    "budget_agent",
    "final_agent",
)

graph.add_edge(
    "final_agent",
    END,
)


# ------------------------------------------------------
# Compile Graph
# ------------------------------------------------------

app = graph.compile()
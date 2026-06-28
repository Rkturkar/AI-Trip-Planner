"""
Shared LLM configuration for the AI Trip Planner.
"""

import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()

# ------------------------------------------------------
# Groq LLM
# ------------------------------------------------------

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.5,
)



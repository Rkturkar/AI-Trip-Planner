"""
AI Trip Planner
FastAPI Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from Backend.routers.health import router as health_router
from Backend.routers.planner import router as planner_router
from Backend.routers.history import router as history_router
from Backend.routers.chat import router as chat_router


# --------------------------------------------------
# FastAPI App
# --------------------------------------------------

app = FastAPI(
    title="AI Trip Planner API",
    version="3.0.0",
    description="AI-powered travel planning using LangGraph and FastAPI.",
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Register Routers
# --------------------------------------------------

app.include_router(
    health_router,
    tags=["Health"],
)

app.include_router(
    planner_router,
    prefix="/planner",
    tags=["Trip Planner"],
)

app.include_router(
    history_router,
    prefix="/history",
    tags=["History"],
)

app.include_router(
    chat_router,
    prefix="/chat",
    tags=["Follow Up Chat"],
)


# --------------------------------------------------
# Root Endpoint
# --------------------------------------------------

@app.get("/")
async def root():
    return {
        "message": "AI Trip Planner API is running 🚀",
        "version": "3.0.0",
        "status": "healthy",
    }
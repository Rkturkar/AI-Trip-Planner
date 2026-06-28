from fastapi import APIRouter

from Backend.schemas.trip import TripRequest
from Backend.services.planner_service import (
    plane_trip,
    stream_trip,
)

router = APIRouter()


@router.post("/plan")
async def plan_trip(req: TripRequest):
    return await plane_trip(req)


@router.post("/plan/stream")
async def plan_trip_stream(req: TripRequest):
    return await stream_trip(req)    
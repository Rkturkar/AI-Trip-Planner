from fastapi import APIRouter

from Backend.schemas.chat import FollowUpRequest
from Backend.services.followup_service import followup_chat

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post("/followup")
async def followup(request: FollowUpRequest):
    return await followup_chat(request)
from fastapi import APIRouter

from Backend.schemas.history import SaveChatRequest
from Backend.services.history_service import (
    save_trip,
    get_trip_history,
    get_trip,
    delete_trip,
)

router = APIRouter()


@router.post("/save")
async def save_history(req: SaveChatRequest):
    return save_trip(req)


@router.get("/{session_id}")
async def history(session_id: str):
    return get_trip_history(session_id)


@router.get("/{session_id}/{chat_id}")
async def history_by_id(session_id: str, chat_id: int):
    return get_trip(chat_id, session_id)


@router.delete("/{session_id}/{chat_id}")
async def delete_history(session_id: str, chat_id: int):
    return delete_trip(chat_id, session_id)
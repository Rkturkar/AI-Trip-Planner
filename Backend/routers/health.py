from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/")
async def root():
    return {
        "message": "AI Trip Planner API is running 🚀",
        "version": "3.0.0"
    }


@router.get("/health")
async def health():
    return {
        "status": "ok"
    }
from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
async def health():
    return {
        "status": "Healthy",
        "service": "Research Assistant AI",
        "version": "0.1.0",
    }

from fastapi import APIRouter

router = APIRouter(
    prefix="/research",
    tags=['Research']
)

@router.post("")
async def research():
    return {
        "info":"Research endpoint is coming."
    }
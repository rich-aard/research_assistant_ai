from fastapi import FastAPI

from backend.app.api import health_router, research_router

app = FastAPI(
    title="Research Assistant AI",
)

app.include_router(health_router)
app.include_router(research_router)

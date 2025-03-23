from fastapi import APIRouter

from app.api.v1.endpoints import health

api_router = APIRouter()

api_router.include_router(health.router)

@api_router.get("/")
async def root():
    """
    Root API v1 endpoint.
    """
    return {"message": "Welcome to SwissHacks API v1"}
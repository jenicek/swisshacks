from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.api import api_router

# Create the main FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for SwissHacks application",
    version="0.1.0",
    docs_url=f"{settings.API_V1_STR}/docs",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Configure CORS - allowing all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API router with the API_V1_STR prefix
app.include_router(api_router, prefix=settings.API_V1_STR)


# Root path response
@app.get("/")
async def main_root():
    """
    Root endpoint that redirects to API documentation.
    """
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "versions": {
            "v1": {
                "url": settings.API_V1_STR,
                "docs": f"{settings.API_V1_STR}/docs"
            }
        }
    }
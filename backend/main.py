from fastapi import FastAPI

from backend.core.config import settings
from backend.modules.health.routes import router as health_router

app=FastAPI(
    title=settings.APP_NAME,
    description="Logged, seguro e rápido",
    version="1.0.0",
    debug=settings.DEBUG,
)

app.include_router(health_router)
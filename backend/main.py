from fastapi import FastAPI

from backend.core.config import settings
from backend.core.telemetry import RequestTelemetryMiddleware, setup_logging
from backend.modules.health.routes import router as health_router
from backend.modules.users.routes import router as users_router
from backend.modules.auth.routes import router as auth_router

setup_logging()

app=FastAPI(
    title=settings.APP_NAME,
    description="Logged, API.",
    version="1.0.0",
    debug=settings.DEBUG,
)

app.add_middleware(RequestTelemetryMiddleware)

app.include_router(health_router)
app.include_router(users_router)
app.include_router(auth_router)

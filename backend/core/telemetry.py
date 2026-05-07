import json
import logging
import time
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from backend.core.config import settings


LOGGER_NAME = "logged.telemetry"


def setup_logging() -> None:
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    logging.getLogger("uvicorn.access").disabled = True
    logging.getLogger("uvicorn.error").setLevel(settings.LOG_LEVEL)


class RequestTelemetryMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        logger = logging.getLogger(LOGGER_NAME)
        request_id = request.headers.get("x-request-id") or str(uuid4())
        started_at = time.perf_counter()
        status_code = 500
        response = None

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception:
            duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
            logger.exception(
                json.dumps(
                    {
                        "event": "http_request_failed",
                        "request_id": request_id,
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": status_code,
                        "duration_ms": duration_ms,
                        "client_ip": request.client.host if request.client else None,
                    }
                )
            )
            raise
        finally:
            if response is not None:
                duration_ms = round((time.perf_counter() - started_at) * 1000, 2)

                event = {
                    "event": "http_request",
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": status_code,
                    "duration_ms": duration_ms,
                    "client_ip": request.client.host if request.client else None,
                    "user_agent": request.headers.get("user-agent"),
                }

                if status_code >= 500:
                    logger.error(json.dumps(event))
                elif status_code >= 400:
                    logger.warning(json.dumps(event))
                else:
                    logger.info(json.dumps(event))

                response.headers["X-Request-ID"] = request_id
                response.headers["X-Process-Time-Ms"] = str(duration_ms)

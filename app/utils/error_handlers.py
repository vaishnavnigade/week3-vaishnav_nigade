import logging
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger("api.errors")


def register_exception_handlers(app: FastAPI) -> None:
    """Register consistent validation and unexpected-error responses."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        trace_id = request.headers.get("X-Request-ID") or str(uuid4())

        logger.warning(
            "validation_error trace_id=%s method=%s path=%s details=%s",
            trace_id,
            request.method,
            request.url.path,
            exc.errors(),
        )

        return JSONResponse(
            status_code=422,
            content={
                "error": "validation_error",
                "message": "Request validation failed",
                "trace_id": trace_id,
                "details": jsonable_encoder(exc.errors()),
            },
        )

    @app.exception_handler(Exception)
    async def unexpected_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        trace_id = request.headers.get("X-Request-ID") or str(uuid4())

        logger.exception(
            "unexpected_error trace_id=%s method=%s path=%s",
            trace_id,
            request.method,
            request.url.path,
        )

        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_server_error",
                "message": "An unexpected error occurred",
                "trace_id": trace_id,
            },
        )
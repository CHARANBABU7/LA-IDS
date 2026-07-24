from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Normalizes all HTTPException responses (404, 409, etc.) into one
    consistent shape the frontend can rely on everywhere.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": True, "status_code": exc.status_code, "message": exc.detail},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Normalizes Pydantic/FastAPI's 422 validation errors into the same shape."""
    return JSONResponse(
        status_code=422,
        content={"error": True, "status_code": 422, "message": "Invalid request data", "details": exc.errors()},
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catches anything unexpected (bugs, DB errors, etc.) so the frontend
    never sees a raw traceback or an inconsistent error shape — even
    for failures nobody explicitly anticipated.
    """
    return JSONResponse(
        status_code=500,
        content={"error": True, "status_code": 500, "message": "An unexpected error occurred."},
    )
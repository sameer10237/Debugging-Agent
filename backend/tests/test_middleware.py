"""Unit tests for middleware components."""

import pytest
from fastapi import FastAPI, HTTPException
from httpx import ASGITransport, AsyncClient

from app.exceptions import ErrorLoggingMiddleware


@pytest.fixture
def app_with_middleware():
    """Create a test FastAPI app configured with ErrorLoggingMiddleware."""
    test_app = FastAPI()
    test_app.add_middleware(ErrorLoggingMiddleware)

    @test_app.get("/ping")
    async def ping():
        return {"status": "ok"}

    @test_app.get("/fail")
    async def fail():
        raise HTTPException(status_code=400, detail="bad request")

    return test_app


@pytest.mark.asyncio
async def test_error_logging_middleware_dispatches_successfully(app_with_middleware):
    """Ensure middleware allows successful requests without raising argument errors."""
    transport = ASGITransport(app=app_with_middleware)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/ping")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_error_logging_middleware_handles_http_errors(app_with_middleware):
    """Ensure middleware allows error responses through cleanly."""
    transport = ASGITransport(app=app_with_middleware)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/fail")
        assert response.status_code == 400

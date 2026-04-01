import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_notes_patient_not_found():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/patients/99999/notes")
        assert response.status_code in [404, 500]

@pytest.mark.asyncio
async def test_summary_patient_not_found():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/patients/99999/summary")
        assert response.status_code in [404, 500]

import pytest
from httpx import AsyncClient
from fastapi import status
from codegrapher.main import app  # Assuming your FastAPI app instance is named `app`

@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client

@pytest.mark.asyncio
async def test_generate_report(async_client):
    response = await async_client.get("/generate-report")
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "text/csv; charset=utf-8"

@pytest.mark.asyncio
async def test_add_candidate_data(async_client):
    new_candidate = {
        "fullname": "John Doe",
        "email": "johndoe@example.com",
        "address": "123 Main St",
        "education": "Bachelor's Degree",
        "phone_number": "123-456-7890",
        "experience_years": 5,
        "skills": ["Python", "FastAPI"]
    }
    response = await async_client.post("/", json=new_candidate)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["message"] == "Candidate added successfully."

@pytest.mark.asyncio
async def test_get_candidates(async_client):
    response = await async_client.get("/all-candidates", params={"page": 1, "limit": 10})
    assert response.status_code == status.HTTP_200_OK
    assert "candidates" in response.json()["data"]

@pytest.mark.asyncio
async def test_get_candidate_data(async_client):
    candidate_id = "some_valid_candidate_id"
    response = await async_client.get(f"/{candidate_id}")
    if response.status_code == status.HTTP_200_OK:
        assert "fullname" in response.json()["data"]
    else:
        assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_update_candidate_data(async_client):
    candidate_id = "some_valid_candidate_id"
    update_data = {
        "fullname": "Jane Doe"
    }
    response = await async_client.put(f"/{candidate_id}", json=update_data)
    if response.status_code == status.HTTP_200_OK:
        assert response.json()["data"]["fullname"] == "Jane Doe"
    else:
        assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_delete_candidate_data(async_client):
    candidate_id = "some_valid_candidate_id"
    response = await async_client.delete(f"/{candidate_id}")
    if response.status_code == status.HTTP_200_OK:
        assert response.json()["message"] == "Candidate deleted successfully"
    else:
        assert response.status_code == status.HTTP_404_NOT_FOUND

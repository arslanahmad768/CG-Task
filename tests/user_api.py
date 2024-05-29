import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from codegrapher.main import app  # assuming your FastAPI app is in main.py
from codegrapher.app.helpers import ResponseModel

@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client

@pytest.fixture
def user_data():
    return {
        "fullname": "Test User",
        "email": "testuser@example.com",
        "city": "Test City",
        "disabled": False,
        "password": "testpassword"
    }

@pytest.mark.asyncio
async def test_add_user_data(async_client, user_data):
    response = await async_client.post("/", json=user_data)
    assert response.status_code == 200
    assert response.json() == ResponseModel(user_data, "User added successfully.")

@pytest.mark.asyncio
async def test_user_login(async_client, user_data):
    # First, add the user to the database
    await async_client.post("/", json=user_data)

    # Then, attempt to log in
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    response = await async_client.post("/token", data=login_data)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_get_current_user(async_client, user_data):
    # First, add the user to the database
    await async_client.post("/", json=user_data)

    # Log in to get the token
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    login_response = await async_client.post("/token", data=login_data)
    token_data = login_response.json()

    # Get the current user using the token
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    response = await async_client.get("/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == user_data["email"]

@pytest.mark.asyncio
async def test_add_user_duplicate_email(async_client, user_data):
    # Add the user to the database
    await async_client.post("/", json=user_data)

    # Attempt to add the same user again
    response = await async_client.post("/", json=user_data)
    assert response.status_code == 400
    assert response.json() == {"detail": "Email already registered"}

@pytest.mark.asyncio
async def test_invalid_login(async_client, user_data):
    # Attempt to log in with invalid credentials
    login_data = {
        "username": user_data["email"],
        "password": "wrongpassword"
    }
    response = await async_client.post("/token", data=login_data)
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}

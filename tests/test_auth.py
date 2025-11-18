import pytest
from httpx import AsyncClient
# from sqlalchemy.ext.asyncio import AsyncSession
# from app.crud.user import user as crud_user

@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    response = await client.post(
        "/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "NewPassword123",
            "full_name": "New User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "password" not in data

@pytest.mark.asyncio
async def test_login_user(client: AsyncClient, test_user): # type: ignore[unused-argument]
    response = await client.post(
        "/auth/login/access-token",
        data={
            "username": "testuser",
            "password": "TestPassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, test_user): # type: ignore[unused-argument]
    # First login to get token
    login_response = await client.post(
        "/auth/login/access-token",
        data={
            "username": "testuser",
            "password": "TestPassword123"
        }
    )
    token = login_response.json()["access_token"]

    # Test authenticated endpoint
    response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"

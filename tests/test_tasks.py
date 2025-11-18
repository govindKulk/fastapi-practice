import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_task(client: AsyncClient, test_user): # type: ignore[unused-argument]
    # Login first
    login_response = await client.post(
        "/auth/login/access-token",
        data={"username": "testuser", "password": "TestPassword123"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create task
    response = await client.post(
        "/tasks/",
        json={
            "title": "Test Task",
            "description": "This is a test task",
            "priority": "high"
        },
        headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["priority"] == "high"
    assert data["status"] == "pending"

@pytest.mark.asyncio
async def test_get_tasks(client: AsyncClient, test_user): # type: ignore[unused-argument]
    # Login and create a task first
    login_response = await client.post(
        "/auth/login/access-token",
        data={"username": "testuser", "password": "TestPassword123"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create task
    await client.post(
        "/tasks/",
        json={"title": "Test Task", "description": "Test description"},
        headers=headers
    )

    # Get tasks
    response = await client.get("/tasks/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Task"

@pytest.mark.asyncio
async def test_update_task(client: AsyncClient, test_user): # type: ignore[unused-argument]
    # Setup
    login_response = await client.post(
        "/auth/login/access-token",
        data={"username": "testuser", "password": "TestPassword123"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create task
    create_response = await client.post(
        "/tasks/",
        json={"title": "Original Title", "description": "Original description"},
        headers=headers
    )
    task_id = create_response.json()["id"]

    # Update task
    response = await client.put(
        f"/tasks/{task_id}",
        json={
            "title": "Updated Title",
            "status": "completed"
        },
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["status"] == "completed"

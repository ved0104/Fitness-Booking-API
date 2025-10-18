# tests/test_auth.py

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_signup_success(client: AsyncClient):
    """Test successful user registration"""
    user_data = {
        "name": "John Doe",
        "email": "[email protected]",
        "password": "password123"
    }
    
    response = await client.post("/api/v1/auth/signup", json=user_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["name"] == user_data["name"]
    assert "id" in data
    assert "hashed_password" not in data  # Password should not be returned


@pytest.mark.asyncio
async def test_signup_duplicate_email(client: AsyncClient):
    """Test that signup with duplicate email fails"""
    user_data = {
        "name": "John Doe",
        "email": "[email protected]",
        "password": "password123"
    }
    
    # First signup
    await client.post("/api/v1/auth/signup", json=user_data)
    
    # Second signup with same email should fail
    response = await client.post("/api/v1/auth/signup", json=user_data)
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_signup_invalid_email(client: AsyncClient):
    """Test signup with invalid email format"""
    user_data = {
        "name": "John Doe",
        "email": "invalid-email",
        "password": "password123"
    }
    
    response = await client.post("/api/v1/auth/signup", json=user_data)
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_signup_short_password(client: AsyncClient):
    """Test signup with password shorter than minimum length"""
    user_data = {
        "name": "John Doe",
        "email": "[email protected]",
        "password": "123"  # Less than 6 characters
    }
    
    response = await client.post("/api/v1/auth/signup", json=user_data)
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user):
    """Test successful login"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user["user_data"]["email"],
            "password": test_user["user_data"]["password"]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, test_user):
    """Test login with incorrect password"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user["user_data"]["email"],
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """Test login with non-existent email"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "[email protected]",
            "password": "somepassword"
        }
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, test_user):
    """Test getting current user info with valid token"""
    response = await client.get(
        "/api/v1/auth/me",
        headers=test_user["headers"]
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user["user_data"]["email"]
    assert data["name"] == test_user["user_data"]["name"]


@pytest.mark.asyncio
async def test_get_current_user_no_token(client: AsyncClient):
    """Test accessing protected endpoint without token fails"""
    response = await client.get("/api/v1/auth/me")
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(client: AsyncClient):
    """Test accessing protected endpoint with invalid token"""
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token_here"}
    )
    
    assert response.status_code == 401

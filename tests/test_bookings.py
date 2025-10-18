# tests/test_bookings.py

import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta
import pytz


@pytest.mark.asyncio
async def test_book_class_success(client: AsyncClient, test_user, test_class):
    """Test successful class booking"""
    booking_data = {
        "class_id": test_class["id"],
        "client_name": "Alice Smith",
        "client_email": "[email protected]"
    }
    
    response = await client.post(
        "/api/v1/bookings/",
        json=booking_data,
        headers=test_user["headers"]
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["class_id"] == test_class["id"]
    assert data["client_name"] == booking_data["client_name"]
    assert data["client_email"] == booking_data["client_email"]
    assert "class_details" in data


@pytest.mark.asyncio
async def test_book_class_no_auth(client: AsyncClient, test_class):
    """Test booking without authentication fails"""
    booking_data = {
        "class_id": test_class["id"],
        "client_name": "Alice Smith",
        "client_email": "[email protected]"
    }
    
    response = await client.post("/api/v1/bookings/", json=booking_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_book_class_duplicate(client: AsyncClient, test_user, test_class):
    """Test that duplicate booking by same user fails"""
    booking_data = {
        "class_id": test_class["id"],
        "client_name": "Alice Smith",
        "client_email": "[email protected]"
    }
    
    # First booking
    response1 = await client.post(
        "/api/v1/bookings/",
        json=booking_data,
        headers=test_user["headers"]
    )
    assert response1.status_code == 201
    
    # Second booking by same user (should fail)
    response2 = await client.post(
        "/api/v1/bookings/",
        json=booking_data,
        headers=test_user["headers"]
    )
    
    assert response2.status_code == 400
    assert "already booked" in response2.json()["detail"].lower()


@pytest.mark.asyncio
async def test_book_class_invalid_id(client: AsyncClient, test_user):
    """Test booking with invalid class ID"""
    booking_data = {
        "class_id": "invalid_id_format",
        "client_name": "Alice Smith",
        "client_email": "[email protected]"
    }
    
    response = await client.post(
        "/api/v1/bookings/",
        json=booking_data,
        headers=test_user["headers"]
    )
    
    assert response.status_code == 400
    assert "invalid" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_book_class_nonexistent(client: AsyncClient, test_user):
    """Test booking non-existent class"""
    booking_data = {
        "class_id": "507f1f77bcf86cd799439011",  # Valid format but doesn't exist
        "client_name": "Alice Smith",
        "client_email": "[email protected]"
    }
    
    response = await client.post(
        "/api/v1/bookings/",
        json=booking_data,
        headers=test_user["headers"]
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_user_bookings_empty(client: AsyncClient, test_user):
    """Test getting bookings when user has no bookings"""
    response = await client.get(
        "/api/v1/bookings/",
        headers=test_user["headers"]
    )
    
    assert response.status_code == 200
    bookings = response.json()
    assert isinstance(bookings, list)
    assert len(bookings) == 0


@pytest.mark.asyncio
async def test_get_user_bookings(client: AsyncClient, test_user, test_class):
    """Test getting user's bookings"""
    # Create a booking first
    booking_data = {
        "class_id": test_class["id"],
        "client_name": "Alice Smith",
        "client_email": "[email protected]"
    }
    await client.post(
        "/api/v1/bookings/",
        json=booking_data,
        headers=test_user["headers"]
    )
    
    # Get bookings
    response = await client.get(
        "/api/v1/bookings/",
        headers=test_user["headers"]
    )
    
    assert response.status_code == 200
    bookings = response.json()
    assert len(bookings) >= 1
    assert bookings[0]["client_name"] == booking_data["client_name"]
    assert bookings[0]["class_details"] is not None


@pytest.mark.asyncio
async def test_get_bookings_no_auth(client: AsyncClient):
    """Test getting bookings without authentication fails"""
    response = await client.get("/api/v1/bookings/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_book_class_full_slots(client: AsyncClient, test_user):
    """Test booking when class is full"""
    # Create class with only 1 slot
    IST = pytz.timezone('Asia/Kolkata')
    future_time = datetime.now(IST) + timedelta(days=7)
    
    class_data = {
        "name": "Full Class",
        "dateTime": future_time.isoformat(),
        "instructor": "Test Instructor",
        "availableSlots": 1
    }
    
    response = await client.post(
        "/api/v1/classes/",
        json=class_data,
        headers=test_user["headers"]
    )
    full_class = response.json()
    
    # Book the only slot
    booking1 = {
        "class_id": full_class["id"],
        "client_name": "First User",
        "client_email": "[email protected]"
    }
    await client.post("/api/v1/bookings/", json=booking1, headers=test_user["headers"])
    
    # Create second user
    user2_data = {
        "name": "Second User",
        "email": "[email protected]",
        "password": "password123"
    }
    await client.post("/api/v1/auth/signup", json=user2_data)
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": user2_data["email"], "password": user2_data["password"]}
    )
    user2_token = login_response.json()["access_token"]
    
    # Try to book the class (should fail - no slots)
    booking2 = {
        "class_id": full_class["id"],
        "client_name": "Second User",
        "client_email": "[email protected]"
    }
    response = await client.post(
        "/api/v1/bookings/",
        json=booking2,
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    
    assert response.status_code == 400
    assert "no available slots" in response.json()["detail"].lower()

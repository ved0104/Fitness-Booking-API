# tests/conftest.py

import pytest
import asyncio
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
from app.main import app
from app.config import settings

# Test database name
TEST_DB_NAME = "fitness_booking_test_db"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_db():
    """Create a test database and clean up after test"""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[TEST_DB_NAME]
    
    # Create indexes
    await db.users.create_index("email", unique=True)
    await db.bookings.create_index([("class_id", 1), ("user_id", 1)], unique=True)
    
    yield db
    
    # Cleanup: Drop all collections
    await db.users.drop()
    await db.fitness_classes.drop()
    await db.bookings.drop()
    client.close()


@pytest.fixture(scope="function")
async def client():
    """Create async HTTP client for testing"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def test_user(client: AsyncClient):
    """Create a test user and return credentials with JWT token"""
    user_data = {
        "name": "Test User",
        "email": "[email protected]",
        "password": "testpass123"
    }
    
    # Signup
    response = await client.post("/api/v1/auth/signup", json=user_data)
    assert response.status_code == 201
    
    # Login to get token
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": user_data["email"], "password": user_data["password"]}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    return {
        "user_data": user_data,
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"}
    }


@pytest.fixture
async def test_class(client: AsyncClient, test_user):
    """Create a test fitness class"""
    import pytz
    from datetime import datetime, timedelta
    
    IST = pytz.timezone('Asia/Kolkata')
    future_time = datetime.now(IST) + timedelta(days=7)
    
    class_data = {
        "name": "Test Yoga Class",
        "dateTime": future_time.isoformat(),
        "instructor": "Test Instructor",
        "availableSlots": 5
    }
    
    response = await client.post(
        "/api/v1/classes/",
        json=class_data,
        headers=test_user["headers"]
    )
    
    assert response.status_code == 201
    return response.json()

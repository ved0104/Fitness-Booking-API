# app/routers/classes.py

from fastapi import APIRouter, Depends, status
from typing import List
from app.schemas.fitness_class import FitnessClassCreate, FitnessClassResponse
from app.services.class_service import ClassService, get_class_service
from app.services.auth_service import get_auth_service
from app.services.auth_service import get_current_user
router = APIRouter(prefix="/api/v1/classes", tags=["Fitness Classes"])


@router.post(
    "/",
    response_model=FitnessClassResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_fitness_class(
    class_data: FitnessClassCreate,
    current_user: dict = Depends(get_current_user),
    class_service: ClassService = Depends(get_class_service)
):
    """
    Create a new fitness class (Authentication required)
    
    - **name**: Class name (e.g., Yoga Flow, HIIT Session, Zumba)
    - **dateTime**: Class date and time in ISO format (e.g., 2025-06-15T10:00:00Z)
    - **instructor**: Instructor name
    - **availableSlots**: Number of available slots (1-100)
    
    All times are automatically converted and stored in IST timezone.
    The class must be scheduled for a future date/time.
    """
    return await class_service.create_class(class_data, current_user)


@router.get("/", response_model=List[FitnessClassResponse])
async def get_upcoming_classes(
    class_service: ClassService = Depends(get_class_service)
):
    """
    Get all upcoming fitness classes
    
    Returns a list of all classes scheduled in the future.
    Classes are sorted by dateTime in ascending order.
    No authentication required - public endpoint.
    """
    return await class_service.get_upcoming_classes()


@router.get("/{class_id}", response_model=FitnessClassResponse)
async def get_class_by_id(
    class_id: str,
    class_service: ClassService = Depends(get_class_service)
):
    """
    Get details of a specific fitness class by ID
    
    - **class_id**: MongoDB ObjectId of the class
    
    Returns detailed information about the requested class.
    No authentication required - public endpoint.
    """
    fitness_class = await class_service.get_class_by_id(class_id)
    
    return FitnessClassResponse(
        id=str(fitness_class["_id"]),
        name=fitness_class["name"],
        dateTime=fitness_class["dateTime"],
        instructor=fitness_class["instructor"],
        availableSlots=fitness_class["availableSlots"],
        totalSlots=fitness_class["totalSlots"],
        created_at=fitness_class["created_at"]
    )

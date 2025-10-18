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
    return await class_service.create_class(class_data, current_user)


@router.get("/", response_model=List[FitnessClassResponse])
async def get_upcoming_classes(
    class_service: ClassService = Depends(get_class_service)
):
    return await class_service.get_upcoming_classes()


@router.get("/{class_id}", response_model=FitnessClassResponse)
async def get_class_by_id(
    class_id: str,
    class_service: ClassService = Depends(get_class_service)
):
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

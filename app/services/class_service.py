# app/services/class_service.py

from typing import List
from fastapi import HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime

from app.database import get_database
from app.schemas.fitness_class import FitnessClassCreate, FitnessClassResponse
from app.utils.timezone import get_ist_now, parse_datetime_to_ist


class ClassService:
    """Service for handling fitness class operations"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.classes_collection = db.fitness_classes
    
    async def create_class(self, class_data: FitnessClassCreate, current_user: dict) -> FitnessClassResponse:
        """Create a new fitness class"""
        # Parse and convert datetime to IST
        try:
            class_datetime = parse_datetime_to_ist(class_data.dateTime)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        # Check if class is in the future
        if class_datetime <= get_ist_now():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Class dateTime must be in the future"
            )
        
        # Create class document
        class_dict = {
            "name": class_data.name,
            "dateTime": class_datetime,
            "instructor": class_data.instructor,
            "availableSlots": class_data.availableSlots,
            "totalSlots": class_data.availableSlots,  # Store original slots count
            "created_at": get_ist_now(),
            "created_by": str(current_user["_id"])
        }
        
        # Insert class into database
        result = await self.classes_collection.insert_one(class_dict)
        
        # Fetch and return created class
        created_class = await self.classes_collection.find_one({"_id": result.inserted_id})
        
        return FitnessClassResponse(
            id=str(created_class["_id"]),
            name=created_class["name"],
            dateTime=created_class["dateTime"],
            instructor=created_class["instructor"],
            availableSlots=created_class["availableSlots"],
            totalSlots=created_class["totalSlots"],
            created_at=created_class["created_at"]
        )
    
    async def get_upcoming_classes(self) -> List[FitnessClassResponse]:
        """Get all upcoming fitness classes"""
        current_time = get_ist_now()
        
        # Query for classes scheduled in the future
        cursor = self.classes_collection.find(
            {"dateTime": {"$gt": current_time}}
        ).sort("dateTime", 1)
        
        classes = await cursor.to_list(length=100)
        
        return [
            FitnessClassResponse(
                id=str(cls["_id"]),
                name=cls["name"],
                dateTime=cls["dateTime"],
                instructor=cls["instructor"],
                availableSlots=cls["availableSlots"],
                totalSlots=cls["totalSlots"],
                created_at=cls["created_at"]
            )
            for cls in classes
        ]
    
    async def get_class_by_id(self, class_id: str) -> dict:
        """Get a class by its ID"""
        try:
            obj_id = ObjectId(class_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid class ID format"
            )
        
        fitness_class = await self.classes_collection.find_one({"_id": obj_id})
        
        if not fitness_class:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class not found"
            )
        
        return fitness_class


def get_class_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> ClassService:
    """Dependency to get class service instance"""
    return ClassService(db)

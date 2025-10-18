# app/services/booking_service.py

from typing import List
from fastapi import HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from app.database import get_database
from app.schemas.booking import BookingCreate, BookingResponse
from app.utils.timezone import parse_datetime_to_ist, get_ist_now


class BookingService:
    """Service for handling booking operations"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.bookings_collection = db.bookings
        self.classes_collection = db.fitness_classes
    
    async def create_booking(self, booking_data: BookingCreate, current_user: dict) -> BookingResponse:
        """Book a slot in a fitness class"""
        # Validate class ID format
        try:
            class_obj_id = ObjectId(booking_data.class_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid class ID format"
            )
        
        # Check if class exists and is in the future
        fitness_class = await self.classes_collection.find_one({"_id": class_obj_id})
        
        if not fitness_class:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class not found"
            )
        
        if parse_datetime_to_ist(fitness_class["dateTime"]) <= get_ist_now():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot book a class that has already started or passed"
            )
        
        # Use atomic operation to prevent race conditions and double booking
        # This ensures that even with concurrent requests, only one succeeds if slots run out
        update_result = await self.classes_collection.find_one_and_update(
            {
                "_id": class_obj_id,
                "availableSlots": {"$gt": 0}  # Only update if slots available
            },
            {
                "$inc": {"availableSlots": -1}  # Atomically decrement available slots
            },
            return_document=True
        )
        
        if not update_result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No available slots for this class"
            )
        
        # Create booking document
        booking_dict = {
            "class_id": class_obj_id,
            "user_id": current_user["_id"],
            "client_name": booking_data.client_name,
            "client_email": booking_data.client_email,
            "booked_at": get_ist_now()
        }
        
        try:
            # Insert booking into database
            # The compound unique index on (class_id, user_id) prevents duplicate bookings
            result = await self.bookings_collection.insert_one(booking_dict)
            
            # Fetch created booking
            created_booking = await self.bookings_collection.find_one({"_id": result.inserted_id})
            
            return BookingResponse(
                id=str(created_booking["_id"]),
                class_id=str(created_booking["class_id"]),
                user_id=str(created_booking["user_id"]),
                client_name=created_booking["client_name"],
                client_email=created_booking["client_email"],
                booked_at=created_booking["booked_at"],
                class_details={
                    "name": fitness_class["name"],
                    "dateTime": fitness_class["dateTime"],
                    "instructor": fitness_class["instructor"]
                }
            )
            
        except DuplicateKeyError:
            # If duplicate booking detected, rollback the slot decrement
            await self.classes_collection.update_one(
                {"_id": class_obj_id},
                {"$inc": {"availableSlots": 1}}
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already booked this class"
            )
    
    async def get_user_bookings(self, current_user: dict) -> List[BookingResponse]:
        """Get all bookings for the authenticated user"""
        # Find all bookings for the user
        cursor = self.bookings_collection.find(
            {"user_id": current_user["_id"]}
        ).sort("booked_at", -1)
        
        bookings = await cursor.to_list(length=100)
        
        # Enrich bookings with class details
        result = []
        for booking in bookings:
            # Fetch class details
            fitness_class = await self.classes_collection.find_one({"_id": booking["class_id"]})
            
            class_details = None
            if fitness_class:
                class_details = {
                    "name": fitness_class["name"],
                    "dateTime": fitness_class["dateTime"],
                    "instructor": fitness_class["instructor"]
                }
            
            result.append(
                BookingResponse(
                    id=str(booking["_id"]),
                    class_id=str(booking["class_id"]),
                    user_id=str(booking["user_id"]),
                    client_name=booking["client_name"],
                    client_email=booking["client_email"],
                    booked_at=booking["booked_at"],
                    class_details=class_details
                )
            )
        
        return result


def get_booking_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> BookingService:
    """Dependency to get booking service instance"""
    return BookingService(db)

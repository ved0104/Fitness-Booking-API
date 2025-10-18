from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class FitnessClassCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Class name (e.g., Yoga Flow, HIIT)")
    dateTime: str = Field(..., description="Class date and time in ISO format (e.g., 2025-06-15T10:00:00Z)")
    instructor: str = Field(..., min_length=2, max_length=100, description="Instructor name")
    availableSlots: int = Field(..., gt=0, le=100, description="Number of available slots")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Yoga Flow",
                "dateTime": "2025-06-15T10:00:00Z",
                "instructor": "John Doe",
                "availableSlots": 20
            }
        }


class FitnessClassResponse(BaseModel):
    id: str
    name: str
    dateTime: datetime
    instructor: str
    availableSlots: int
    totalSlots: int
    created_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "name": "HIIT Session",
                "dateTime": "2025-06-18T08:00:00+05:30",
                "instructor": "Jane Smith",
                "availableSlots": 10,
                "totalSlots": 20,
                "created_at": "2025-06-10T15:30:00+05:30"
            }
        }


class FitnessClassUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    dateTime: Optional[str] = None
    instructor: Optional[str] = Field(None, min_length=2, max_length=100)
    availableSlots: Optional[int] = Field(None, gt=0, le=100)

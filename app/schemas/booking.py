from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class BookingCreate(BaseModel):
    class_id: str = Field(..., description="ID of the fitness class to book")
    client_name: str = Field(..., min_length=2, max_length=100, description="Client name for booking")
    client_email: EmailStr = Field(..., description="Client email for booking")
    
    class Config:
        json_schema_extra = {
            "example": {
                "class_id": "507f1f77bcf86cd799439011",
                "client_name": "Alice",
                "client_email": "[email protected]"
            }
        }


class BookingResponse(BaseModel):
    id: str
    class_id: str
    user_id: str
    client_name: str
    client_email: EmailStr
    booked_at: datetime
    class_details: Optional[dict] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439012",
                "class_id": "507f1f77bcf86cd799439011",
                "user_id": "507f1f77bcf86cd799439010",
                "client_name": "Alice",
                "client_email": "[email protected]",
                "booked_at": "2025-06-15T14:30:00+05:30",
                "class_details": {
                    "name": "Yoga Flow",
                    "dateTime": "2025-06-18T10:00:00+05:30",
                    "instructor": "John Doe"
                }
            }
        }

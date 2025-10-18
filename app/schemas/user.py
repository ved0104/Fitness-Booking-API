# app/schemas/user.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserSignup(BaseModel):
    """Schema for user registration"""
    name: str = Field(..., min_length=2, max_length=100, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=6, max_length=72, description="User's password (min 6 characters)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "[email protected]",
                "password": "securepass123"
            }
        }


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "[email protected]",
                "password": "securepass123"
            }
        }


class UserResponse(BaseModel):
    """Schema for user response"""
    id: str
    name: str
    email: EmailStr
    created_at: datetime
    is_active: bool
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "name": "John Doe",
                "email": "[email protected]",
                "created_at": "2025-06-15T10:00:00+05:30",
                "is_active": True
            }
        }


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class TokenData(BaseModel):
    """Schema for token payload data"""
    email: Optional[str] = None

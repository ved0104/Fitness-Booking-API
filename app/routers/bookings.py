# app/routers/bookings.py

from fastapi import APIRouter, Depends, status
from typing import List
from app.schemas.booking import BookingCreate, BookingResponse
from app.services.booking_service import BookingService, get_booking_service
from app.services.auth_service import get_auth_service
from app.services.auth_service import get_current_user
router = APIRouter(
    prefix="/api/v1/bookings",
    tags=["Bookings"]
)


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def book_class(
    booking_data: BookingCreate,
    current_user: dict = Depends(get_current_user),
    booking_service: BookingService = Depends(get_booking_service)
):
    """
    Book a slot in a fitness class (Authentication required)
    
    - **class_id**: ID of the fitness class to book
    - **client_name**: Name for the booking
    - **client_email**: Email for the booking
    
    Features:
    - Prevents double booking (same user cannot book same class twice)
    - Atomic slot decrement to prevent race conditions
    - Validates class exists and is in the future
    - Checks available slots before booking
    
    Returns booking confirmation with class details.
    """
    booking = await booking_service.create_booking(booking_data, current_user)
    return booking


@router.get("/", response_model=List[BookingResponse])
async def get_my_bookings(
    current_user: dict = Depends(get_current_user),
    booking_service: BookingService = Depends(get_booking_service)
):
    """
    Get all bookings for the authenticated user
    
    Returns list of all bookings made by the current user.
    Bookings are sorted by booking date in descending order (newest first).
    Each booking includes enriched class details (name, dateTime, instructor).
    """
    bookings = await booking_service.get_user_bookings(current_user)
    return bookings

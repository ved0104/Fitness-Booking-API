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
    booking = await booking_service.create_booking(booking_data, current_user)
    return booking


@router.get("/", response_model=List[BookingResponse])
async def get_my_bookings(
    current_user: dict = Depends(get_current_user),
    booking_service: BookingService = Depends(get_booking_service)
):
    bookings = await booking_service.get_user_bookings(current_user)
    return bookings

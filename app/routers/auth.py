# app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user import UserSignup, UserLogin, UserResponse, Token
from app.services.auth_service import AuthService, get_auth_service
from app.services.auth_service import get_current_user
router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserSignup,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user
    
    - **name**: User's full name (2-100 characters)
    - **email**: User's email address (must be unique)
    - **password**: User's password (minimum 6 characters)
    
    Returns the created user information (without password)
    """
    return await auth_service.signup(user_data)


@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.login(user_data)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)
):
    return UserResponse(
        id=str(current_user["_id"]),
        name=current_user["name"],
        email=current_user["email"],
        created_at=current_user["created_at"],
        is_active=current_user["is_active"]
    )

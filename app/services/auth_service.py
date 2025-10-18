from fastapi import HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.database import get_database
from app.schemas.user import UserSignup, UserLogin, UserResponse, Token
from app.utils.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
    oauth2_scheme
)
from app.utils.timezone import get_ist_now

class AuthService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.users_collection = db.users

    async def signup(self, user_data: UserSignup) -> UserResponse:
        existing_user = await self.users_collection.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        user_dict = {
            "name": user_data.name,
            "email": user_data.email,
            "hashed_password": get_password_hash(user_data.password),
            "created_at": get_ist_now(),
            "is_active": True
        }
        result = await self.users_collection.insert_one(user_dict)
        created_user = await self.users_collection.find_one({"_id": result.inserted_id})
        return UserResponse(
            id=str(created_user["_id"]),
            name=created_user["name"],
            email=created_user["email"],
            created_at=created_user["created_at"],
            is_active=created_user["is_active"]
        )

    async def login(self, user_data: UserLogin) -> Token:
        user = await self.users_collection.find_one({"email": user_data.email})
        if not user or not verify_password(user_data.password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user account"
            )
        access_token = create_access_token(data={"sub": user["email"]})
        return Token(access_token=access_token, token_type="bearer")

    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> dict:
        payload = decode_access_token(token)
        email = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = await self.users_collection.find_one({"email": email})
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        return user

async def get_auth_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> AuthService:
    return AuthService(db)

async def get_current_user(
    auth_service: AuthService = Depends(get_auth_service),
    token: str = Depends(oauth2_scheme)
) -> dict:
    return await auth_service.get_current_user(token)

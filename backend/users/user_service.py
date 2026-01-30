from typing import Optional
from .user_models import UserInDB, UserCreate
from passlib.context import CryptContext
from motor.motor_asyncio import AsyncIOMotorDatabase
import uuid
from datetime import datetime

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

class UserService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.users

    def verify_password(self, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return pwd_context.hash(password)

    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        user_doc = await self.collection.find_one({"email": email})
        if user_doc:
            return UserInDB(**user_doc)
        return None

    async def create_user(self, user: UserCreate) -> UserInDB:
        hashed_password = self.get_password_hash(user.password)
        db_user = UserInDB(
            **user.model_dump(exclude={"password"}),
            hashed_password=hashed_password
        )
        await self.collection.insert_one(db_user.model_dump())
        return db_user

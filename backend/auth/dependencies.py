from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from auth.auth_service import SECRET_KEY, ALGORITHM
from users.user_models import TokenData, User
from users.user_service import UserService
from motor.motor_asyncio import AsyncIOMotorClient
import os

# We need a way to get the DB instance. For now, we'll create a new client or reuse if possible.
# In a real app, use dependency injection properly.
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

async def get_db():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    try:
        yield db
    finally:
        pass # Client is managed by pool, but we could close it if we created a new one every time. Motor handles pooling.

async def get_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

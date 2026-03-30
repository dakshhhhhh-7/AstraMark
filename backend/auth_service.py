"""
Enhanced Authentication Service with Refresh Tokens
"""
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
import uuid
import secrets

from config import settings

# Password hashing
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

class TokenData(BaseModel):
    email: Optional[EmailStr] = None
    token_type: Optional[str] = None

class RefreshTokenData(BaseModel):
    user_id: str
    jti: str  # JWT ID for token revocation

class AuthTokens(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class UserInDB(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str] = None
    hashed_password: str
    is_active: bool = True
    is_premium: bool = False
    subscription_plan: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({
        "exp": expire,
        "type": "access",
        "iat": datetime.now(timezone.utc),
        "jti": str(uuid.uuid4())
    })
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

def create_refresh_token(user_id: str) -> str:
    """Create JWT refresh token"""
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    jti = str(uuid.uuid4())
    
    to_encode = {
        "sub": user_id,
        "exp": expire,
        "type": "refresh",
        "iat": datetime.now(timezone.utc),
        "jti": jti
    }
    return jwt.encode(to_encode, settings.jwt_refresh_secret_key, algorithm=settings.jwt_algorithm)

def create_auth_tokens(user: UserInDB) -> AuthTokens:
    """Create both access and refresh tokens"""
    access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
    refresh_token = create_refresh_token(user.id)
    
    return AuthTokens(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60
    )

def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    """Verify and decode JWT token"""
    try:
        secret_key = (
            settings.jwt_secret_key if token_type == "access" 
            else settings.jwt_refresh_secret_key
        )
        
        payload = jwt.decode(token, secret_key, algorithms=[settings.jwt_algorithm])
        
        # Verify token type
        if payload.get("type") != token_type:
            raise JWTError("Invalid token type")
        
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_user_by_email(db, email: str) -> Optional[UserInDB]:
    """Fetch user by email from database"""
    user_doc = await db.users.find_one({"email": email})
    if not user_doc:
        return None
    
    return UserInDB(
        id=str(user_doc.get("id", user_doc.get("_id"))),
        email=user_doc["email"],
        full_name=user_doc.get("full_name"),
        hashed_password=user_doc["hashed_password"],
        is_active=user_doc.get("is_active", True),
        is_premium=user_doc.get("is_premium", False),
        subscription_plan=user_doc.get("subscription_plan"),
        created_at=user_doc.get("created_at", datetime.now(timezone.utc)),
        last_login=user_doc.get("last_login")
    )

async def get_user_by_id(db, user_id: str) -> Optional[UserInDB]:
    """Fetch user by ID from database"""
    user_doc = await db.users.find_one({"id": user_id})
    if not user_doc:
        return None
    
    return UserInDB(
        id=str(user_doc.get("id", user_doc.get("_id"))),
        email=user_doc["email"],
        full_name=user_doc.get("full_name"),
        hashed_password=user_doc["hashed_password"],
        is_active=user_doc.get("is_active", True),
        is_premium=user_doc.get("is_premium", False),
        subscription_plan=user_doc.get("subscription_plan"),
        created_at=user_doc.get("created_at", datetime.now(timezone.utc)),
        last_login=user_doc.get("last_login")
    )

async def authenticate_user(db, email: str, password: str) -> Optional[UserInDB]:
    """Authenticate user with email and password"""
    user = await get_user_by_email(db, email)
    if not user or not user.is_active:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    # Update last login
    await db.users.update_one(
        {"id": user.id},
        {"$set": {"last_login": datetime.now(timezone.utc)}}
    )
    
    return user

# Token blacklist (in production, use Redis)
revoked_tokens = set()

async def revoke_token(jti: str):
    """Revoke a token by adding its JTI to blacklist"""
    revoked_tokens.add(jti)

async def is_token_revoked(jti: str) -> bool:
    """Check if token is revoked"""
    return jti in revoked_tokens

class AuthService:
    """Authentication service class"""
    
    def __init__(self, db):
        self.db = db
    
    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> UserInDB:
        """Get current authenticated user"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = verify_token(token, "access")
            email: str = payload.get("sub")
            jti: str = payload.get("jti")
            
            if email is None or jti is None:
                raise credentials_exception
            
            # Check if token is revoked
            if await is_token_revoked(jti):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has been revoked"
                )
            
        except JWTError:
            raise credentials_exception
        
        user = await get_user_by_email(self.db, email)
        if user is None or not user.is_active:
            raise credentials_exception
        
        return user
    
    async def refresh_access_token(self, refresh_token: str) -> AuthTokens:
        """Refresh access token using refresh token"""
        try:
            payload = verify_token(refresh_token, "refresh")
            user_id: str = payload.get("sub")
            jti: str = payload.get("jti")
            
            if user_id is None or jti is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
            
            # Check if refresh token is revoked
            if await is_token_revoked(jti):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token has been revoked"
                )
            
            user = await get_user_by_id(self.db, user_id)
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found or inactive"
                )
            
            # Revoke old refresh token
            await revoke_token(jti)
            
            # Create new tokens
            return create_auth_tokens(user)
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
    
    async def logout(self, access_token: str, refresh_token: str):
        """Logout user by revoking tokens"""
        try:
            # Revoke access token
            access_payload = verify_token(access_token, "access")
            await revoke_token(access_payload.get("jti"))
            
            # Revoke refresh token
            refresh_payload = verify_token(refresh_token, "refresh")
            await revoke_token(refresh_payload.get("jti"))
            
        except JWTError:
            # Tokens might be invalid, but that's okay for logout
            pass
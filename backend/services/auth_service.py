"""
Authentication Service
Handles user registration, login, password hashing, and JWT token generation
"""

import bcrypt
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional, Dict
from sqlalchemy.orm import Session
from models.db_models import User
from pydantic import BaseModel, EmailStr
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Pydantic Models for request/response
class UserRegister(BaseModel):
    """User registration request"""
    name: str
    email: EmailStr
    password: str

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response (without password)"""
    id: int
    name: Optional[str]
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str
    user: UserResponse


class AuthService:
    """Service for authentication operations"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    @staticmethod
    def create_access_token(user_id: int, email: str, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        if expires_delta is None:
            expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        expire = datetime.utcnow() + expires_delta
        to_encode = {
            "user_id": user_id,
            "email": email,
            "exp": expire,
            "iat": datetime.utcnow()
        }
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[Dict]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: int = payload.get("user_id")
            email: str = payload.get("email")
            if user_id is None or email is None:
                return None
            return {"user_id": user_id, "email": email}
        except JWTError:
            return None

    @staticmethod
    def register_user(db: Session, user: UserRegister) -> Optional[User]:
        """Register new user"""
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            return None  # User already exists

        # Create new user
        hashed_password = AuthService.hash_password(user.password)
        new_user = User(
            name=user.name,
            email=user.email,
            password_hash=hashed_password
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print(f"✓ User registered: {user.email} (ID: {new_user.id})")
        return new_user

    @staticmethod
    def login_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user and return user if valid"""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None  # User not found

        if not AuthService.verify_password(password, user.password_hash):
            return None  # Password incorrect

        print(f"✓ User logged in: {email} (ID: {user.id})")
        return user

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()

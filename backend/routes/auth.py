"""
Authentication Routes
Register, login, and user profile endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from services.auth_service import (
    AuthService,
    UserRegister,
    UserLogin,
    TokenResponse,
    UserResponse,
)
from middleware.auth_middleware import get_current_user, get_current_user_required
from models.db_models import get_db, User
from typing import Optional

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user
    Returns JWT token on successful registration
    """
    # Register user
    new_user = AuthService.register_user(db, user)

    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Generate JWT token
    access_token = AuthService.create_access_token(
        user_id=new_user.id,
        email=new_user.email
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(new_user)
    }


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login user with email and password
    Returns JWT token on successful login
    """
    # Authenticate user
    user = AuthService.login_user(db, credentials.email, credentials.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Generate JWT token
    access_token = AuthService.create_access_token(
        user_id=user.id,
        email=user.email
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user)
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Get current user information (optional auth)
    Returns user details if authenticated, or null if not
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    return UserResponse.from_orm(current_user)


@router.get("/validate-token")
def validate_token(
    current_user: User = Depends(get_current_user_required)
):
    """
    Validate JWT token
    Returns user info if token is valid
    """
    return {
        "valid": True,
        "user": UserResponse.from_orm(current_user)
    }


@router.post("/logout")
def logout():
    """
    Logout endpoint (client-side JWT removal)
    Just returns success message
    """
    return {
        "message": "Logged out successfully",
        "status": "success"
    }

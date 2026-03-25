"""
JWT Middleware
Validates JWT tokens and provides current user context
"""

from fastapi import HTTPException, status, Header, Depends
from typing import Optional
from sqlalchemy.orm import Session
from services.auth_service import AuthService
from models.db_models import get_db, User


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Dependency to get current authenticated user from JWT token
    If token is invalid or missing, returns None (optional auth)
    """
    if not authorization:
        return None

    try:
        # Extract token from "Bearer <token>"
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return None

        # Verify token
        payload = AuthService.verify_token(token)
        if not payload:
            return None

        user_id = payload.get("user_id")
        user = AuthService.get_user_by_id(db, user_id)
        return user

    except Exception:
        return None


async def get_current_user_required(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user (REQUIRED)
    Raises 401 Unauthorized if token is missing or invalid
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Extract token from "Bearer <token>"
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify token
        payload = AuthService.verify_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = payload.get("user_id")
        user = AuthService.get_user_by_id(db, user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )

        return user

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )

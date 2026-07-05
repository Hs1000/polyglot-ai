"""
Authentication API.

Endpoints
---------
POST /register
POST /login
GET  /me
"""

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.core.security import (
    get_current_active_user,
)
from app.models.user import User
from app.schemas.auth import (
    Token,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.services.auth_service import AuthService
from app.services.email_service import send_welcome_email
from db.postgres import get_db


router = APIRouter()


# ==========================================================
# Register
# ==========================================================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: UserRegister,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Register a new user.
    """

    try:

        user = AuthService.register(
            db=db,
            payload=payload,
        )

        background_tasks.add_task(send_welcome_email, user.email, user.name)

        return user

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ==========================================================
# Login
# ==========================================================

@router.post(
    "/login",
    response_model=Token,
)
def login(
    payload: UserLogin,
    db: Session = Depends(get_db),
):
    """
    Authenticate user.
    """

    try:

        result = AuthService.login(
            db=db,
            payload=payload,
        )

        return {
            "access_token": result["access_token"],
            "token_type": result["token_type"],
        }

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


# ==========================================================
# Current User
# ==========================================================

@router.get(
    "/me",
    response_model=UserResponse,
)
def get_current_user(
    current_user: User = Depends(
        get_current_active_user,
    ),
):
    """
    Return authenticated user.
    """

    return current_user
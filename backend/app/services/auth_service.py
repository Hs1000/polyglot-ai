"""
Authentication service.

Contains all authentication business logic.
"""

from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import (
    UserLogin,
    UserRegister,
)
from app.services.email_service import send_welcome_email


class AuthService:
    """
    Authentication business logic.
    """

    @staticmethod
    def get_user_by_email(
        db: Session,
        email: str,
    ) -> User | None:
        """
        Fetch user by email.
        """

        return (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

    @staticmethod
    def register(
        db: Session,
        payload: UserRegister,
    ) -> User:
        """
        Register a new user.
        """

        existing_user = AuthService.get_user_by_email(
            db,
            payload.email,
        )

        if existing_user:
            raise ValueError(
                "Email already registered."
            )

        user = User(
            name=payload.name,
            email=payload.email,
            hashed_password=hash_password(
                payload.password
            ),
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        send_welcome_email(to_email=user.email, name=user.name)

        return user

    @staticmethod
    def authenticate(
        db: Session,
        payload: UserLogin,
    ) -> User:
        """
        Authenticate a user.
        """

        user = AuthService.get_user_by_email(
            db,
            payload.email,
        )

        if user is None:
            raise ValueError(
                "Invalid email or password."
            )

        if not verify_password(
            payload.password,
            user.hashed_password,
        ):
            raise ValueError(
                "Invalid email or password."
            )

        return user

    @staticmethod
    def login(
        db: Session,
        payload: UserLogin,
    ) -> dict:
        """
        Authenticate and return JWT.
        """

        user = AuthService.authenticate(
            db,
            payload,
        )

        access_token = create_access_token(
            user,
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user,
        }
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.sessions import get_db
from app.schemas.user_schema import (
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.services import user_service
from app.utils.exceptions import (
    AlreadyExistsError,
    InvalidCredentialsError,
)
from app.utils.security import create_access_token


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    payload: UserRegister,
    db: Session = Depends(get_db),
):
    """Register a new customer account."""

    try:
        user = user_service.register_user(db, payload)

    except AlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    return {
        "email": user.email,
        "message": "User registered successfully",
    }


@router.post("/login", response_model=TokenResponse)
def login_user(
    payload: UserLogin,
    db: Session = Depends(get_db),
):
    """Authenticate the user and return a signed JWT."""

    try:
        user = user_service.login_user(db, payload)

    except InvalidCredentialsError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
            headers={"WWW-Authenticate": "Bearer"},
        ) from error

    access_token = create_access_token(
        subject=str(user.id),
        role=user.role,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "email": user.email,
        "role": user.role,
        "message": "Login successful",
    }
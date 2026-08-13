from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from app.db.sessions import get_db
from app.models.user import User
from app.utils.security import bearer_scheme, decode_access_token


def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Return the database user represented by the Bearer JWT."""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # No Authorization header or an unsupported authentication scheme.
    if credentials is None:
        raise credentials_exception

    try:
        # HTTPBearer provides the raw JWT through credentials.credentials.
        payload = decode_access_token(credentials.credentials)

        subject = payload.get("sub")
        if subject is None:
            raise credentials_exception

        user_id = int(subject)

    except (InvalidTokenError, TypeError, ValueError) as error:
        raise credentials_exception from error

    user = db.get(User, user_id)

    if user is None:
        raise credentials_exception

    return user
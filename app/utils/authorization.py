from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status

from app.models.user import User
from app.utils.auth import get_current_user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*allowed_roles: str) -> Callable:
    """
    Create a reusable dependency that allows only selected roles.

    Example:
        Depends(require_roles("admin"))
        Depends(require_roles("admin", "support"))
    """
    normalized_roles = {role.lower() for role in allowed_roles}

    def role_checker(current_user: CurrentUser) -> User:
        user_role = current_user.role.lower()

        if user_role not in normalized_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )

        return current_user

    return role_checker
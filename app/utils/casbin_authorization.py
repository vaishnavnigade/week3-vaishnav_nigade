from collections.abc import Callable
from pathlib import Path
from typing import Annotated

import casbin
from fastapi import Depends, HTTPException, status

from app.models.user import User
from app.utils.auth import get_current_user


# Locate the Casbin configuration files relative to the app directory.
APP_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = APP_DIR / "policies" / "model.conf"
POLICY_PATH = APP_DIR / "policies" / "policy.csv"


# Load the Casbin model and policy definitions once when the application starts.
enforcer = casbin.Enforcer(str(MODEL_PATH), str(POLICY_PATH))


# Reusable type alias for the authenticated user from the JWT.
CurrentUser = Annotated[User, Depends(get_current_user)]


def require_casbin_policy(resource: str, action: str) -> Callable:
    """Create a FastAPI dependency that enforces a Casbin policy."""

    def policy_checker(current_user: CurrentUser) -> User:
        user_role = current_user.role.lower()

        is_allowed = enforcer.enforce(
            user_role,
            resource,
            action.upper(),
        )

        if not is_allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Role '{user_role}' is not authorized for "
                    f"{action.upper()} {resource}"
                ),
            )

        return current_user

    return policy_checker


def enforce_order_abac(current_user: User, order_owner_id: int) -> None:
    """
    Enforce ABAC for order access.

    The decision uses user attributes from the JWT/database and
    the resource owner attribute from the order record.
    """

    privileged_roles = {"admin", "support"}

    is_privileged_user = current_user.role.lower() in privileged_roles
    is_order_owner = current_user.id == order_owner_id

    if not is_privileged_user and not is_order_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to access this order",
        )
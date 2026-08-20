
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.sessions import get_db
from app.models.user import User
from app.schemas.cart_schema import (
    CartItemCreate,
    CartItemRead,
    CartItemUpdate,
)
from app.services import cart_service
from app.utils.auth import get_current_user
from app.utils.exceptions import NotFoundError, OutOfStockError


router = APIRouter(
    prefix="/carts",
    tags=["Cart"],
)


@router.post(
    "/items",
    response_model=CartItemRead,
    status_code=status.HTTP_201_CREATED,
)
def add_to_cart(
    payload: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a product to the authenticated customer's cart."""

    try:
        return cart_service.add_to_cart(
            db,
            current_user.id,
            payload,
        )
    except NotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except OutOfStockError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get(
    "/items",
    response_model=list[CartItemRead],
)
def list_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return only the authenticated customer's cart."""

    return cart_service.list_cart(
        db,
        current_user.id,
    )


@router.put(
    "/items/{cart_item_id}",
    response_model=CartItemRead,
)
def update_cart_item(
    cart_item_id: int,
    payload: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update the quantity of an owned cart item."""

    try:
        return cart_service.update_cart_item(
            db=db,
            user_id=current_user.id,
            cart_item_id=cart_item_id,
            data=payload,
        )
    except NotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except OutOfStockError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.delete(
    "/items/{cart_item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_from_cart(
    cart_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove an owned cart item."""

    try:
        cart_service.remove_from_cart(
            db,
            current_user.id,
            cart_item_id,
        )
    except NotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

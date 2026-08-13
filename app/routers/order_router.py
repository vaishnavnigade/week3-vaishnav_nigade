from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.sessions import get_db
from app.models.user import User
from app.schemas.order_schema import OrderRead
from app.services import order_service
from app.utils.auth import get_current_user
from app.utils.exceptions import NotFoundError, OutOfStockError
from app.utils.authorization import require_roles
from app.services.notification_service import send_order_confirmation
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.async_sessions import get_async_db
from app.repositories import async_order_repository
from app.schemas.order_schema import OrderSummaryRead
from app.utils.authorization import require_roles


router = APIRouter(prefix="/orders", tags=["Orders"])


# Customer checkout.
# The user ID comes from the validated JWT, not from the URL.
@router.post(
    "/checkout",
    response_model=OrderRead,
    status_code=status.HTTP_201_CREATED,
)
def checkout(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return order_service.create_order_from_cart(
            db=db,
            user_id=current_user.id,
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


# Customer can view only their own order history.
# Keep this route before /{order_id}.
@router.get("/me", response_model=list[OrderRead])
def list_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return order_service.list_orders(
        db=db,
        user_id=current_user.id,
    )


# View one order.
# Customers can view their own orders.
# Admin and support users can view any order.
@router.get("/{order_id}", response_model=OrderRead)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        order = order_service.get_order(db, order_id)
    except NotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    allowed_global_roles = {"admin", "support"}

    if (
        current_user.role not in allowed_global_roles
        and order.user_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this order",
        )

    return order

@router.get(
    "/admin/all",
    response_model=list[OrderRead],
    dependencies=[Depends(require_roles("admin", "support"))],
)
def list_all_orders(db: Session = Depends(get_db)):
    """Allow admin and support users to view all customer orders."""
    return order_service.list_all_orders(db)

@router.post(
    "/checkout",
    response_model=OrderRead,
    status_code=status.HTTP_201_CREATED,
)
def checkout(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        order = order_service.create_order_from_cart(
            db=db,
            user_id=current_user.id,
        )

        background_tasks.add_task(
            send_order_confirmation,
            order.id,
            current_user.email,
        )

        return order

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
    "/admin/async-summary",
    response_model=OrderSummaryRead,
    dependencies=[Depends(require_roles("admin", "support"))],
)
async def get_async_order_summary(
    db: AsyncSession = Depends(get_async_db),
):
    """Return order metrics using an asynchronous DB session."""

    return await async_order_repository.get_order_summary(db)
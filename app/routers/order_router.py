
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.db.async_sessions import get_async_db
from app.db.sessions import get_db
from app.models.user import User
from app.repositories import async_order_repository
from app.schemas.order_schema import OrderRead, OrderSummaryRead
from app.services import order_service
from app.services.notification_service import send_notification
from app.utils.auth import get_current_user
from app.utils.authorization import require_roles
from app.utils.exceptions import NotFoundError, OutOfStockError


router = APIRouter(prefix="/orders", tags=["Orders"])


# Customer checkout.
# The customer ID comes from the JWT token, not from the URL.
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

        # Send confirmation after the response workflow is completed.
        background_tasks.add_task(
          send_notification,
          current_user.email,
          f"Order {order.id} confirmed successfully.",
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


# Customers can view only their own order history.
@router.get(
    "/me",
    response_model=list[OrderRead],
)
def list_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return order_service.list_orders(
        db=db,
        user_id=current_user.id,
    )


# Admin and support users can view all orders.
@router.get(
    "/admin/all",
    response_model=list[OrderRead],
    dependencies=[Depends(require_roles("admin", "support"))],
)
def list_all_orders(db: Session = Depends(get_db)):
    return order_service.list_all_orders(db)


# Async order-summary endpoint.
# This demonstrates asynchronous database access.
@router.get(
    "/admin/async-summary",
    response_model=OrderSummaryRead,
    dependencies=[Depends(require_roles("admin", "support"))],
)
async def get_async_order_summary(
    db: AsyncSession = Depends(get_async_db),
):
    return await async_order_repository.get_order_summary(db)


# Customers can view their own orders.
# Admin and support users can view any order.
# Keep this dynamic route after all fixed routes.
@router.get(
    "/{order_id}",
    response_model=OrderRead,
)
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

    user_role = current_user.role.lower()

    is_privileged_user = user_role in {"admin", "support"}
    is_order_owner = order.user_id == current_user.id

    if not is_privileged_user and not is_order_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this order",
        )

    return order



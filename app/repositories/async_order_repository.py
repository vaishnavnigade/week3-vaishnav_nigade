from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order


async def get_order_summary(db: AsyncSession) -> dict[str, int | float]:
    """Return order metrics using non-blocking database queries."""

    total_orders = await db.scalar(
        select(func.count(Order.id))
    )

    pending_orders = await db.scalar(
        select(func.count(Order.id)).where(
            Order.status == "pending"
        )
    )

    total_revenue = await db.scalar(
        select(func.coalesce(func.sum(Order.total_amount), 0))
    )

    return {
        "total_orders": total_orders or 0,
        "pending_orders": pending_orders or 0,
        "total_revenue": total_revenue or 0,
    }
import logging

logger = logging.getLogger("api.notifications")


def send_order_confirmation(order_id: int, email: str) -> None:
    """Simulate sending an order-confirmation notification."""
    logger.info(
        "Order confirmation notification sent",
        extra={
            "order_id": order_id,
            "customer_email": email,
            "event": "order_confirmation",
        },
    )
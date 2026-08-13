import logging
import time


logger = logging.getLogger("api.notifications")


def send_notification(
    email: str,
    message: str,
) -> None:
    """Simulate sending a notification in a background thread."""

    logger.info(
        "notification_started",
        extra={
            "event": "notification_started",
            "customer_email": email,
            "notification_message": message,
        },
    )

    # Simulate a slow email or notification provider.
    time.sleep(3)

    logger.info(
        "notification_sent",
        extra={
            "event": "notification_sent",
            "customer_email": email,
            "notification_message": message,
        },
    )


def send_order_confirmation(
    order_id: int,
    email: str,
) -> None:
    """Log an order-confirmation notification."""

    logger.info(
        "order_confirmation_sent",
        extra={
            "order_id": order_id,
            "customer_email": email,
            "event": "order_confirmation",
        },
    )

import logging

from app.services.notification_service import send_order_confirmation


def test_order_confirmation_notification_is_logged(caplog) -> None:
    caplog.set_level(
        logging.INFO,
        logger="api.notifications",
    )

    send_order_confirmation(
        order_id=101,
        email="customer@example.com",
    )

    assert "Order confirmation notification sent" in caplog.text
    assert "order_confirmation" in caplog.text
    assert "101" in caplog.text
    assert "customer@example.com" in caplog.text

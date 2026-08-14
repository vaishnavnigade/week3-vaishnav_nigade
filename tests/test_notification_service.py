import logging

from app.services.notification_service import send_order_confirmation


def test_order_confirmation_notification_is_logged(caplog) -> None:
    """Verify that the order-confirmation event is logged."""

    caplog.set_level(
        logging.INFO,
        logger="api.notifications",
    )

    send_order_confirmation(
        order_id=101,
        email="customer@example.com",
    )

    records = [
        record
        for record in caplog.records
        if record.name == "api.notifications"
    ]

    assert len(records) == 1
    assert records[0].message == "order_confirmation_sent"
    assert records[0].order_id == 101
    assert records[0].customer_email == "customer@example.com"
    assert records[0].event == "order_confirmation"
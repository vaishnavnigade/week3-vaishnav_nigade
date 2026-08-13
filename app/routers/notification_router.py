from fastapi import APIRouter, BackgroundTasks, Depends, status

from app.models.user import User
from app.schemas.notification_schema import NotificationRequest
from app.services.notification_service import send_notification
from app.utils.authorization import require_roles


router = APIRouter(
    prefix="/api/notifications",
    tags=["Notifications"],
)


@router.post(
    "/send",
    status_code=status.HTTP_202_ACCEPTED,
)
def schedule_notification(
    payload: NotificationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(
        require_roles("admin", "support")
    ),
):
    """
    Schedule a notification without blocking the response.

    Admin and Support users can manually trigger notifications.
    Automatic customer order notifications are triggered from checkout.
    """

    background_tasks.add_task(
        send_notification,
        payload.email,
        payload.message,
    )

    return {
        "status": "Notification scheduled",
        "email": payload.email,
        "requested_by": current_user.email,
    }
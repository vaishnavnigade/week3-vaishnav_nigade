from pydantic import BaseModel, EmailStr, Field


class NotificationRequest(BaseModel):
    """Payload used to schedule a notification."""

    email: EmailStr
    message: str = Field(
        min_length=1,
        max_length=500,
    )
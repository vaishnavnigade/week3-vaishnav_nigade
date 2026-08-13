from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.models.user import User
from app.services.payment_service import (
    PaymentGatewayError,
    PaymentUnavailableError,
    process_payment as call_payment_gateway,
)
from app.utils.auth import get_current_user


router = APIRouter(prefix="/payments", tags=["Payments"])


class PaymentRequest(BaseModel):
    """Request body accepted by the simulated payment gateway."""

    amount_cents: int = Field(gt=0)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    token: str = Field(min_length=1)


@router.post("/process")
async def process_payment(
    payload: PaymentRequest,
    current_user: User = Depends(get_current_user),
):
    """Process a payment through the external payment service."""

    try:
        payment_result = await call_payment_gateway(
            amount_cents=payload.amount_cents,
            currency=payload.currency,
            token=payload.token,
        )

    except PaymentUnavailableError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error

    except PaymentGatewayError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        ) from error

    return {
        "user_id": current_user.id,
        "message": "Payment request completed",
        "payment": payment_result,
    }
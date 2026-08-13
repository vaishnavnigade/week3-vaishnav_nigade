from uuid import uuid4

from fastapi import FastAPI
from pydantic import BaseModel, Field


app = FastAPI(title="Mock Payment Gateway")


class ChargeRequest(BaseModel):
    """Request payload accepted by the simulated payment gateway."""

    amount_cents: int = Field(gt=0)
    currency: str = "INR"
    token: str


@app.post("/charge")
async def charge_payment(request: ChargeRequest) -> dict:
    """Simulate an approved or declined payment."""

    if request.token == "tok_declined":
        return {
            "status": "declined",
            "transaction_id": None,
            "message": "Payment was declined",
        }

    return {
        "status": "approved",
        "transaction_id": str(uuid4()),
        "amount_cents": request.amount_cents,
        "currency": request.currency,
        "message": "Payment approved",
    }
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class PaymentState(Enum):
    pending = "pending"
    authorized = "authorized"
    rejected = "rejected"
    cancelled = "cancelled"
    closing = "closing"
    completed = "completed"


class PaymentRequest(BaseModel):
    amount: int
    payment_profile_id: str
    state: PaymentState = PaymentState.pending


class Payment(PaymentRequest):
    created_at: datetime = Field(default_factory=datetime.utcnow)

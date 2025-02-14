from fastapi import APIRouter
from faststream.kafka.fastapi import KafkaRouter

from api.payments.models import PaymentRequest, Payment, PaymentState

router = KafkaRouter("localhost:9092", prefix="/payments")
# router = APIRouter(prefix="/payments")


@router.subscriber("payments")
async def handle_payment_event(payment: Payment) -> Payment | None:
    if payment.state == PaymentState.pending:
        print(f"got payment {payment}")
        payment.state = PaymentState.authorizing
        await router.broker.publish(payment, topic="payments")
    else:
        print("*** payment aged ***")


@router.post("/")
async def create_payment(payment: PaymentRequest) -> Payment:
    retval = Payment(
        amount=payment.amount, payment_profile_id=payment.payment_profile_id
    )
    # await handle_payment_event(retval)
    await router.broker.publish(retval, topic="payments")

    return retval

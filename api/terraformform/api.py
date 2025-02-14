from typing import Annotated

from fastapi import Depends
from fasthx.htmy import HTMY
from faststream.kafka.fastapi import KafkaRouter

from api.terraformform.ui import IndexPage
from api.terraformform.models import (
    Service,
    Property,
    ValueType,
    Module,
    ServiceSpec,
    ServiceSpecCreate,
)
from api.terraformform.local_module_service import (
    LocalModuleService,
    get_local_module_service,
)


router = KafkaRouter("localhost:9092", prefix="/terraform")
# router = APIRouter(prefix="/payments")

htmy = HTMY(
    # Register a request processor that adds a user-agent key to the htmy context.
    request_processors=[
        lambda request: {"user-agent": request.headers.get("user-agent")},
    ]
)


# @router.subscriber("payments")
# async def handle_payment_event(payment: Payment) -> Payment | None:
#    if payment.state == PaymentState.pending:
#        print(f"got payment {payment}")
#        payment.state = PaymentState.authorized
#        await router.broker.publish(payment, topic="payments")
#    else:
#        print("*** payment aged ***")


@router.get("/")
@htmy.page(lambda _: IndexPage())
def index() -> None:
    """index"""


ServiceSpecs = []


@router.post("/catalog", response_model_exclude_none=True)
def create_service_spec(
    spec: ServiceSpecCreate,
    module_service: Annotated[LocalModuleService, Depends(get_local_module_service)],
) -> ServiceSpec:
    out = ServiceSpec(
        title=spec.title,
        description=spec.description,
        features=[],
        modules=[],
        variables={},
        outputs={},
    )
    for label, modref in spec.modules.items():
        mod = module_service.modules.get(modref.id)
        if not mod:
            # TODO figure out logging
            print(
                f"Coulnt find {modref.id} in {module_service.modules.keys()}")
            continue
        out.modules.append(mod)
        if modref.optional:
            out.features.append(mod)
        if modref.configurable:
            # TODO this needs to be fleshed out with actual logic
            out.variables = {**out.variables, **mod.variables}
        # TODO this needs to be fleshed out with actual logic
        out.outputs = {**out.outputs, **mod.outputs}
    out.variables = {**out.variables, **spec.additional_variables}
    ServiceSpecs.append(out)
    return out


@router.get("/catalog", response_model_exclude_none=True)
def service_catalog() -> list[ServiceSpec]:
    return ServiceSpecs


@router.get("/modules", response_model_exclude_none=True)
def module_catalog(
    service: Annotated[LocalModuleService, Depends(get_local_module_service)],
) -> list[Module]:
    return service.list_modules()

    # @router.post("/")
    # async def create_payment(payment: PaymentRequest) -> Payment:
    #    retval = Payment(
    #        amount=payment.amount, payment_profile_id=payment.payment_profile_id
    #    )
    #    # await handle_payment_event(retval)
    #    await router.broker.publish(retval, topic="payments")
    #
    #    return retval

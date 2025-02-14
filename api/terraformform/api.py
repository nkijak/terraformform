from typing import Annotated, Any

from fastapi import Depends
from fasthx.htmy import HTMY
from faststream.kafka.fastapi import KafkaRouter

from api.terraformform.ui import IndexPage
from api.terraformform.models import (
    Module,
    ServiceSpec,
    ServiceSpecCreate,
    ServiceOrderReceipt,
    ServiceOrderRequest,
    Service,
)
from api.terraformform.local_module_service import (
    LocalModuleService,
    get_local_module_service,
)
from api.mongo import BlockingMongoService, local_blocking_mongo


router = KafkaRouter("localhost:9092", prefix="/terraform")
service_spec_commands = router.publisher("service-spec.commands")
service_order_commands = router.publisher("service-order.commands")
service_order_events = router.publisher("service-order.events")

htmy = HTMY(
    # Register a request processor that adds a user-agent key to the htmy context.
    request_processors=[
        lambda request: {"user-agent": request.headers.get("user-agent")},
    ]
)


@router.subscriber("service-spec.commands")
@router.publisher("service-spec.events")
async def handle_service_spec_creation(
    spec: ServiceSpec,
    mongo: Annotated[BlockingMongoService, Depends(local_blocking_mongo)],
) -> dict[str, Any]:
    breakpoint()
    record, was_created = mongo.upsert(
        "service-spec", spec.content.model_dump())
    return record


@router.subscriber("service-order.commands")
@router.publisher("service-order.events")
async def handle_service_order_command(
    receipt: ServiceOrderReceipt,
    mongo: Annotated[BlockingMongoService, Depends(local_blocking_mongo)],
) -> dict[str, Any]:
    record, was_created = mongo.upsert(
        "service-order-receipt", receipt.model_dump())
    return record


@router.subscriber("service-order.events")
@router.publisher("service.events")
async def create_service_for_service_order(
    order: ServiceOrderReceipt,
    mongo: Annotated[BlockingMongoService, Depends(local_blocking_mongo)],
) -> Service | None:
    if order.status != "accepted":
        return
    spec = mongo.get("service_specs", order.service_spec_id)
    print(spec)
    # spec = ServiceSpec(**spec_dict)

    service = Service(
        title=spec.get("title", "<no title>"),
        description=spec.get("description", "<no description>"),
        properties=order.propertyValues,
    )
    record, was_insert = mongo.upsert("services", service.model_dump())
    order.service_id = service.id
    order.status = "created"
    await service_order_events.publish(order, headers={"action": "updated"})
    return service


@router.get("/")
@htmy.page(lambda _: IndexPage())
def index() -> None:
    """index"""


ServiceSpecs = []


@router.post("/catalog", response_model_exclude_none=True)
async def create_service_spec(
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
    await service_spec_commands.publish(out.model_dump_json())
    return out


@router.get("/catalog", response_model_exclude_none=True)
def service_catalog() -> list[ServiceSpec]:
    return ServiceSpecs


@router.get("/modules", response_model_exclude_none=True)
def module_catalog(
    service: Annotated[LocalModuleService, Depends(get_local_module_service)],
) -> list[Module]:
    return service.list_modules()


@router.post("/service", response_model_exclude_none=True)
async def request_onboarding(request: ServiceOrderRequest) -> ServiceOrderReceipt:
    receipt = ServiceOrderReceipt.from_request(request)
    await service_order_commands.publish(receipt)
    return receipt

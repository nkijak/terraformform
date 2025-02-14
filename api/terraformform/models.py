from datetime import datetime
from enum import StrEnum
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, computed_field

UUIDField = Field(default_factory=lambda: uuid4().hex)


class ValueType(StrEnum):
    integer = "integer"
    object = "object"
    string = "string"
    array = "array"
    boolean = "boolean"


class Property(BaseModel):
    description: str
    type: ValueType
    exclusiveMinimum: int | None = None
    minumum: int | None = None
    # todo these aren't part of spec, but here to facilitate tf
    default: str | None = None


class Array(Property):
    items_type: ValueType
    minItems: int | None = None
    uniqueItems: int | None = None


class PropertyValue(Property):
    value: Any


class Service(BaseModel):
    id: str = UUIDField
    title: str
    description: str
    properties: dict[str, PropertyValue]
    type_: str = "object"
    required: list[str] | None = None
    status: Literal[
        "pending", "inialized", "planned", "failed", "applied", "running"
    ] = "pending"


class ServiceOrderRequest(BaseModel):
    service_spec_id: str
    requested_at: datetime = Field(default_factory=lambda: datetime.utcnow())
    featureValues: dict[str, bool]
    propertyValues: dict[str, PropertyValue]


class ServiceOrderReceipt(ServiceOrderRequest):
    id: str = UUIDField
    status: Literal["rejected", "accepted", "created"] = "accepted"
    service_id: str | None = None

    @staticmethod
    def from_request(request: ServiceOrderRequest) -> "ServiceOrderReceipt":
        return ServiceOrderReceipt(
            service_spec_id=request.service_spec_id,
            featureValues=request.featureValues,
            requested_at=request.requested_at,
            propertyValues=request.propertyValues,
        )


# internal


class Module(BaseModel):
    name: str
    source: str
    variables: dict[str, Property] | None = None
    outputs: dict[str, Property] | None = None

    @computed_field
    @property
    def id(self) -> str:
        return ".".join(self.source.split("/"))


class ModuleUsage(BaseModel):
    id: str = UUIDField
    module_id: str
    variableValues: dict[str, Any] | None = None
    outputs: dict[str, Any] | None = None


class ModuleRef(BaseModel):
    id: str
    optional: bool = False
    configurable: bool = True


class ServiceSpecCreate(BaseModel):
    title: str
    description: str
    modules: dict[str, ModuleRef]
    additional_variables: dict[str, Property]


class ServiceSpec(BaseModel):
    id: str = UUIDField
    title: str
    description: str
    features: list[Module]
    modules: list[(str, Module)]
    variables: dict[str, Property]
    outputs: dict[str, Property]

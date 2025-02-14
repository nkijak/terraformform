from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, computed_field

UUIDField = Field(default_factory=lambda: str(uuid4()))


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


class Service(BaseModel):
    id: str = UUIDField
    title: str
    description: str
    properties: dict[str, Property]
    type_: str = "object"
    required: list[str] | None = None


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

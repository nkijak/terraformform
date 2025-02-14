from pathlib import Path
from api.terraformform.models import Module, Property, ValueType

import hcl2


class LocalModuleService:
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.modules: dict[str, Module] = {}

    def read_module(self, path: Path) -> Module:
        variables = {}
        for f in path.glob("*.tf"):
            with open(f, "r") as raw_tf:
                tf = hcl2.load(raw_tf)

            if tfvariables := tf.get("variable"):
                for var_dict in tfvariables:
                    for name, props in var_dict.items():
                        match props.get("type"):
                            case "string":
                                vtype = ValueType.string
                            case "boolean":
                                vtype = ValueType.boolean
                            case "integer":
                                vtype = ValueType.integer
                            case _:
                                vtype = None
                        if vtype:
                            variables[name] = Property(
                                description=props.get(
                                    "description", "<missing>"),
                                type=vtype,
                                default=props.get("default"),
                            )
            outputs = {}
            if tfoutputs := tf.get("output"):
                for vdict in tfoutputs:
                    for name, props in vdict.items():
                        outputs[name] = Property(
                            description=props.get("description", "n/a"),
                            type=ValueType.string,
                            read_only=True,
                        )
        module = Module(
            name=path.name,
            source=path.as_posix(),
            variables=variables,
            outputs=outputs,
        )
        self.modules[module.id] = module

    def list_modules(self) -> list[Module]:
        if not self.modules:
            for child in self.base_path.iterdir():
                if child.is_dir():
                    self.read_module(child)
        return self.modules.values()


def get_local_module_service() -> LocalModuleService:
    service = LocalModuleService(Path("api/terraformform/terraform/modules"))
    service.list_modules()
    return service

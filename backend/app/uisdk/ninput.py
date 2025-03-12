from typing import List, Dict
from app.uisdk.baseComponent import (
    BaseComponent,
    ComponentVariable,
    ComponentVariableType,
)


class NInput(BaseComponent):
    def __init__(
        self,
        type: str,
        value: str,
        size: str,
        clearable: bool,
        slots: Dict,
    ):
        super().__init__(
            Type="NInput",
            Props={
                "type": ComponentVariable(Type=ComponentVariableType.Value, Value=type),
                "value": ComponentVariable(Type=ComponentVariableType.Ref, Value=value),
                "size": ComponentVariable(Type=ComponentVariableType.Value, Value=size),
                "clearable": ComponentVariable(
                    Type=ComponentVariableType.Value, Value=clearable
                ),
            },
            Slots=slots,
        )
        pass

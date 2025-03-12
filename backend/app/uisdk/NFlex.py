from typing import List, Dict
from app.uisdk.baseComponent import (
    BaseComponent,
    ComponentVariable,
    ComponentVariableType,
)


class NFlex(BaseComponent):
    def __init__(
        self,
        align: str,
        justify: str,
        vertical: bool,
        wrap: bool,
        slots: Dict,
    ):
        super().__init__(
            Type="NFlex",
            Props={
                "align": ComponentVariable(
                    Type=ComponentVariableType.Value, Value=align
                ),
                "justify": ComponentVariable(
                    Type=ComponentVariableType.Value, Value=justify
                ),
                "vertical": ComponentVariable(
                    Type=ComponentVariableType.Value, Value=vertical
                ),
                "wrap": ComponentVariable(Type=ComponentVariableType.Value, Value=wrap),
            },
            Slots=slots,
        )

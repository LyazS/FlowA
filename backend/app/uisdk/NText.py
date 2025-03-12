from typing import List, Dict
from app.uisdk.baseComponent import (
    BaseComponent,
    ComponentVariable,
    ComponentVariableType,
)


class NText(BaseComponent):
    def __init__(
        self,
        type: str,
        strong: bool,
        italic: bool,
        underline: bool,
        delete: bool,
        code: bool,
        depth: int,
        slots: Dict,
    ):
        super().__init__(
            Type="NText",
            Props={
                "type": ComponentVariable(Type=ComponentVariableType.Value, Value=type),
                "strong": ComponentVariable(
                    Type=ComponentVariableType.Value, Value=strong
                ),
                "italic": ComponentVariable(
                    Type=ComponentVariableType.Value, Value=italic
                ),
                "underline": ComponentVariable(
                    Type=ComponentVariableType.Value, Value=underline
                ),
                "delete": ComponentVariable(
                    Type=ComponentVariableType.Value, Value=delete
                ),
                "code": ComponentVariable(Type=ComponentVariableType.Value, Value=code),
                "depth": ComponentVariable(
                    Type=ComponentVariableType.Value, Value=depth
                ),
            },
            Slots=slots,
        )

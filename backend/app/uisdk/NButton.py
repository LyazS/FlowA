from typing import List, Dict
from app.uisdk.baseComponent import (
    BaseComponent,
    ComponentVariable,
    ComponentVariableType,
)


class NButton(BaseComponent):
    def __init__(
        self,
        block: bool,
        bordered: bool,
        circle: bool,
        color: str,
        dashed: bool,
        ghost: bool,
        round: bool,
        size: str,
        strong: bool,
        text: bool,
        text_color: str,
        type: str,
        level: str,
        slots: Dict,
    ):
        Props = {
            "block": ComponentVariable(Type=ComponentVariableType.Value, Value=block),
            "bordered": ComponentVariable(
                Type=ComponentVariableType.Value, Value=bordered
            ),
            "circle": ComponentVariable(Type=ComponentVariableType.Value, Value=circle),
            "color": ComponentVariable(Type=ComponentVariableType.Value, Value=color),
            "dashed": ComponentVariable(Type=ComponentVariableType.Value, Value=dashed),
            "ghost": ComponentVariable(Type=ComponentVariableType.Value, Value=ghost),
            "round": ComponentVariable(Type=ComponentVariableType.Value, Value=round),
            "size": ComponentVariable(Type=ComponentVariableType.Value, Value=size),
            "strong": ComponentVariable(Type=ComponentVariableType.Value, Value=strong),
            "text": ComponentVariable(Type=ComponentVariableType.Value, Value=text),
            "text-color": ComponentVariable(
                Type=ComponentVariableType.Value, Value=text_color
            ),
            "type": ComponentVariable(Type=ComponentVariableType.Value, Value=type),
        }
        if level == "secondary":
            Props["secondary"] = ComponentVariable(
                Type=ComponentVariableType.Value, Value=True
            )
        elif level == "tertiary":
            Props["tertiary"] = ComponentVariable(
                Type=ComponentVariableType.Value, Value=True
            )
        elif level == "quaternary":
            Props["quaternary"] = ComponentVariable(
                Type=ComponentVariableType.Value, Value=True
            )

        super().__init__(
            Type="NButton",
            Props=Props,
            Slots=slots,
        )
        pass

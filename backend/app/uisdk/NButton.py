from typing import List, Dict, Optional
from app.uisdk.VFUISchemas import PropVar, PropVarType, NormalComponent
from app.uisdk.VFUIUtils import cvtProps2PropVar


class NButton(NormalComponent):
    def __init__(
        self,
        block: bool | PropVar,
        bordered: bool | PropVar,
        circle: bool | PropVar,
        color: str | PropVar,
        dashed: bool | PropVar,
        ghost: bool | PropVar,
        round: bool | PropVar,
        size: str | PropVar,
        strong: bool | PropVar,
        text: bool | PropVar,
        text_color: str | PropVar,
        type: str | PropVar,
        level: str = "",
        slots: Optional[Dict] = None,
    ):
        Props = {
            "block": block,
            "bordered": bordered,
            "circle": circle,
            "color": color,
            "dashed": dashed,
            "ghost": ghost,
            "round": round,
            "size": size,
            "strong": strong,
            "text": text,
            "text_color": text_color,
            "type": type,
        }
        if level == "secondary":
            Props["secondary"] = True
        elif level == "tertiary":
            Props["tertiary"] = True
        elif level == "quaternary":
            Props["quaternary"] = True

        super().__init__(
            Type="NButton",
            Props=cvtProps2PropVar(Props),
            Slots=slots,
        )
        pass

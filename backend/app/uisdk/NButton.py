from typing import List, Dict, Optional, Literal
from app.uisdk.VFUISchemas import PropVar, PropVarType, NormalComponent


class NButton(NormalComponent):
    def __init__(
        self,
        block: bool | PropVar = False,
        bordered: bool | PropVar = True,
        circle: bool | PropVar = False,
        color: Optional[
            str | PropVar
        ] = None,  # 按钮颜色（支持形如 #FFF， #FFFFFF， yellow，rgb(0, 0, 0) 的颜色）
        dashed: bool | PropVar = False,
        ghost: bool | PropVar = False,
        iconPlacement: PropVar | Literal["left", "right"] = "left",
        round: bool | PropVar = False,
        size: PropVar | Literal["tiny", "small", "medium", "large"] = "medium",
        strong: bool | PropVar = False,
        text: bool | PropVar = False,
        text_color: Optional[
            str | PropVar
        ] = None,  # 按钮文字颜色（支持形如 #FFF， #FFFFFF， yellow，rgb(0, 0, 0) 的颜色）
        type: (
            PropVar
            | Literal[
                "default", "tertiary", "primary", "success", "info", "warning", "error"
            ]
        ) = "default",
        level: Optional[Literal["secondary", "tertiary", "quaternary"]] = None,
        slots: Optional[Dict] = None,
    ):
        Props = {
            "block": block,
            "bordered": bordered,
            "circle": circle,
            "color": color,
            "dashed": dashed,
            "ghost": ghost,
            "icon-placement": iconPlacement,
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
            Props=Props,
            Slots=slots,
        )
        pass

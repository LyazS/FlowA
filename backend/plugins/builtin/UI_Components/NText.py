from typing import List, Dict, Optional, Literal
from app.uisdk.VFUISchemas import (
    PropVar,
    ReadOnlyPropVar,
    NormalComponent,
    ConditionType,
    CompareCondition,
    LogicalCondition,
    DirectCondition,
    Condition,
)


class NText(NormalComponent):
    def __init__(
        self,
        type: (
            ReadOnlyPropVar | Literal["default", "success", "info", "warning", "error"]
        ) = "default",
        strong: bool | ReadOnlyPropVar = False,
        italic: bool | ReadOnlyPropVar = False,
        underline: bool | ReadOnlyPropVar = False,
        delete: bool | ReadOnlyPropVar = False,
        code: bool | ReadOnlyPropVar = False,
        depth: ReadOnlyPropVar | Literal[1, 2, 3, "1", "2", "3"] = None,
        style: Optional[Dict] = None,
        slots: Optional[Dict] = None,
        IfCondition: Optional[Condition] = None,
    ):
        super().__init__(
            Type="NText",
            Props={
                "type": type,
                "strong": strong,
                "italic": italic,
                "underline": underline,
                "delete": delete,
                "code": code,
                "depth": depth,
                "style": style,
            },
            Slots=slots,
            IfCondition=IfCondition,
        )

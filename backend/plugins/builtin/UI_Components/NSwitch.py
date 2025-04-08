from pydantic import BaseModel
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


class NSwitch(NormalComponent):
    def __init__(
        self,
        size: ReadOnlyPropVar | Literal["small", "medium", "large"] = "medium",
        value: Optional[str | PropVar] = None,
        style: Optional[Dict] = None,
        slots: Optional[Dict] = None,
        IfCondition: Optional[Condition] = None,
    ):
        super().__init__(
            Type="NSwitch",
            Props={
                "size": size,
                "value": value,
                "style": style,
            },
            Slots=slots,
            IfCondition=IfCondition,
        )
        pass

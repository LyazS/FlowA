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


class NFlex(NormalComponent):
    def __init__(
        self,
        align: Optional[str | PropVar] = None,
        justify: str | PropVar = "start",
        vertical: Optional[bool | PropVar] = False,
        size: Optional[
            PropVar | Literal["small", "medium", "large"] | float | List[float]
        ] = "medium",
        wrap: bool | PropVar = True,
        style: Optional[Dict] = None,
        otherProps: Dict = {},
        slots: Optional[Dict] = None,
        IfCondition: Optional[Condition] = None,
    ):
        super().__init__(
            Type="NFlex",
            Props={
                "align": align,
                "justify": justify,
                "vertical": vertical,
                "size": size,
                "wrap": wrap,
                "style": style,
                **otherProps,
            },
            Slots=slots,
            IfCondition=IfCondition,
        )

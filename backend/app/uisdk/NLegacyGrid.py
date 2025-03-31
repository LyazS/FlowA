from typing import List, Dict, Optional, Union
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


class NRow(NormalComponent):
    def __init__(
        self,
        xGap: Union[int | PropVar] = 0,
        yGap: Union[int | PropVar] = 0,
        style: Optional[Dict] = None,
        slots: Optional[Dict] = None,
        IfCondition: Optional[Condition] = None,
    ):
        super().__init__(
            Type="NRow",
            Props={
                "gutter": [xGap, yGap],
                "style": style,
            },
            Slots=slots,
            IfCondition=IfCondition,
        )


class NCol(NormalComponent):
    def __init__(
        self,
        span: Union[int | PropVar] = 1,
        offset: Union[int | PropVar] = 0,
        push: Union[int | PropVar] = 0,
        pull: Union[int | PropVar] = 0,
        style: Optional[Dict] = None,
        slots: Optional[Dict] = None,
        IfCondition: Optional[Condition] = None,
    ):
        super().__init__(
            Type="NCol",
            Props={
                "span": span,
                "offset": offset,
                "push": push,
                "pull": pull,
                "style": style,
            },
            Slots=slots,
            IfCondition=IfCondition,
        )

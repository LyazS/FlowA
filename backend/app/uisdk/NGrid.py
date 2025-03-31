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


class NGrid(NormalComponent):
    def __init__(
        self,
        cols: Union[int | PropVar] = 24,
        xGap: Union[int | PropVar] = 0,
        yGap: Union[int | PropVar] = 0,
        style: Optional[Dict] = None,
        slots: Optional[Dict] = None,
        IfCondition: Optional[Condition] = None,
    ):
        super().__init__(
            Type="NGrid",
            Props={
                "cols": cols,
                "x-gap": xGap,
                "y-gap": yGap,
                "style": style,
            },
            Slots=slots,
            IfCondition=IfCondition,
        )


class NGridItem(NormalComponent):
    def __init__(
        self,
        offset: Union[int | PropVar] = 0,
        span: Union[int | PropVar] = 1,
        style: Optional[Dict] = None,
        slots: Optional[Dict] = None,
        IfCondition: Optional[Condition] = None,
    ):
        super().__init__(
            Type="NGridItem",
            Props={
                "offset": offset,
                "span": span,
                "style": style,
            },
            Slots=slots,
            IfCondition=IfCondition,
        )

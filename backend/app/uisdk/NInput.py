from typing import List, Dict, Optional
from app.uisdk.VFUISchemas import PropVar, PropVarType, NormalComponent
from app.uisdk.VFUIUtils import cvtProps2PropVar


class NInput(NormalComponent):
    def __init__(
        self,
        type: str | PropVar,
        value: str | PropVar,
        size: str | PropVar,
        clearable: bool | PropVar,
        slots: Optional[Dict] = None,
    ):
        super().__init__(
            Type="NInput",
            Props=cvtProps2PropVar(
                {
                    "type": type,
                    "value": value,
                    "size": size,
                    "clearable": clearable,
                }
            ),
            Slots=slots,
        )
        pass

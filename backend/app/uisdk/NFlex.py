from typing import List, Dict, Optional
from app.uisdk.VFUISchemas import PropVar, PropVarType, NormalComponent
from app.uisdk.VFUIUtils import cvtProps2PropVar


class NFlex(NormalComponent):
    def __init__(
        self,
        align: str | PropVar,
        justify: str | PropVar,
        vertical: bool | PropVar,
        wrap: bool | PropVar,
        slots: Optional[Dict] = None,
    ):
        super().__init__(
            Type="NFlex",
            Props=cvtProps2PropVar(
                {
                    "align": align,
                    "justify": justify,
                    "vertical": vertical,
                    "wrap": wrap,
                }
            ),
            Slots=slots,
        )

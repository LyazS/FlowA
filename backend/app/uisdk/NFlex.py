from typing import List, Dict, Optional
from app.uisdk.VFUISchemas import PropVar, PropVarType, BaseComponent


class NFlex(BaseComponent):
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
            Props={
                "align": align,
                "justify": justify,
                "vertical": vertical,
                "wrap": wrap,
            },
            Slots=slots,
        )

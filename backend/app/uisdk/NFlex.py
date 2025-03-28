from typing import List, Dict, Optional
from app.uisdk.VFUISchemas import PropVar, ReadOnlyPropVar, NormalComponent


class NFlex(NormalComponent):
    def __init__(
        self,
        align: Optional[str | PropVar] = None,
        justify: str | PropVar = "start",
        vertical: Optional[bool | PropVar] = False,
        wrap: bool | PropVar = True,
        style: Optional[Dict] = None,
        slots: Optional[Dict] = None,
    ):
        super().__init__(
            Type="NFlex",
            Props={
                "align": align,
                "justify": justify,
                "vertical": vertical,
                "wrap": wrap,
                "style": style,
            },
            Slots=slots,
        )

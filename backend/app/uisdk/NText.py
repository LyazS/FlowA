from typing import List, Dict, Optional
from app.uisdk.VFUISchemas import PropVar, PropVarType, BaseComponent


class NText(BaseComponent):
    def __init__(
        self,
        type: str | PropVar,
        strong: bool | PropVar,
        italic: bool | PropVar,
        underline: bool | PropVar,
        delete: bool | PropVar,
        code: bool | PropVar,
        depth: int | PropVar,
        slots: Optional[Dict] = None,
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
            },
            Slots=slots,
        )

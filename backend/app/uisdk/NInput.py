from pydantic import BaseModel
from typing import List, Dict, Optional, Literal
from app.uisdk.VFUISchemas import PropVar, ReadOnlyPropVar, NormalComponent


class NInputAutoSize(BaseModel):
    minRows: Optional[int] = None
    maxRows: Optional[int] = None
    pass


class NInput(NormalComponent):
    def __init__(
        self,
        autosize: bool | NInputAutoSize | ReadOnlyPropVar = False,
        clearable: bool | ReadOnlyPropVar = False,
        defaultValue: Optional[str | ReadOnlyPropVar] = None,
        maxlength: Optional[int | ReadOnlyPropVar] = None,
        minlength: Optional[int | ReadOnlyPropVar] = None,
        round: bool | ReadOnlyPropVar = False,
        rows: Optional[int | ReadOnlyPropVar] = None,
        showCount: bool | ReadOnlyPropVar = False,
        showPasswordOn: Optional[
            ReadOnlyPropVar | Literal["click", "mousedown"]
        ] = None,
        size: ReadOnlyPropVar | Literal["tiny", "small", "medium", "large"] = "medium",
        type: ReadOnlyPropVar | Literal["text", "password", "textarea"] = "text",
        value: Optional[str | PropVar] = None,
        slots: Optional[Dict] = None,
    ):
        super().__init__(
            Type="NInput",
            Props={
                "autosize": autosize,
                "clearable": clearable,
                "default-value": defaultValue,
                "maxlength": maxlength,
                "minlength": minlength,
                "round": round,
                "rows": rows,
                "show-count": showCount,
                "show-password-on": showPasswordOn,
                "size": size,
                "type": type,
                "value": value,
            },
            Slots=slots,
        )
        pass

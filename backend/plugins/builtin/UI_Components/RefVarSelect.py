from typing import Optional, Dict, Union, Literal
from app.uisdk import *


class UI_RefVarSelect(NormalComponent):
    def __init__(
        self,
        value: VModelProp,
        options: ReadOnlyPropVar,
        size: Optional[ReadOnlyPropVar | Literal["medium", "tiny", "small", "large"]] = None,
        placeholder: Optional[str | ReadOnlyPropVar] = '请选择',
        style: Optional[Dict] = None,
        IfCondition: Condition = None,
    ):
        super().__init__(
            Type="RefVarSelect",
            Props={
                "style": style,
                "value": value,
                "options": options,
                "size": size,
                "placeholder": placeholder,
            },
            Slots=None,
            IfCondition=IfCondition,
        )

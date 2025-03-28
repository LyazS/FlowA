from app.uisdk import *
from typing import Literal


class Header(NormalComponent):
    def __init__(
        self,
        type: Literal["default", "success", "info", "warning", "error"] = "default",
        level: Literal[1, 2, 3, 4, 5, 6] = 3,
        text: str | ReadOnlyPropVar = "标题",
    ):
        ntextslot = None
        if isinstance(text, str):
            ntextslot = SpanComponent(Type=ComponentType.VALUE, Data=text)
        elif isinstance(text, ValueProp):
            ntextslot = SpanComponent(Type=ComponentType.VALUE, Data=text.Data)
        elif isinstance(text, VBindProp):
            ntextslot = SpanComponent(Type=ComponentType.VBIND, Data=text.Data)
        else:
            raise ValueError("text must be str or ValueProp")

        super().__init__(
            Type=f"NH{level}",
            Props={
                "prefix": "bar",
                "type": type,
                "style": {
                    "margin-top": 0,
                    "margin-bottom": 0,
                },
            },
            Slots={
                "default": NText(
                    type=type,
                    slots={"default": ntextslot},
                ),
            },
        )

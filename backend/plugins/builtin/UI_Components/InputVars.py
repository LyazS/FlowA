from app.uisdk import *
from .Header import Header


class UI_InputVars(NFlex):
    def __init__(self):
        super().__init__(
            vertical=True,
            slots={
                "default": NFlex(
                    vertical=False,
                    wrap=False,
                    justify="space-between",
                    style={"align-content": "center", "align-items": "center"},
                    slots={
                        "default": [
                            Header(type="success", text="输入变量"),
                            NButton(
                                text=True,
                                slots={
                                    "default": SpanComponent(
                                        Type=ComponentType.VALUE, Data="添加"
                                    ),
                                    "icon": NormalComponent(Type="Add"),
                                },
                            ),
                        ]
                    },
                ),
            },
        )


EXPORT_UI = UI_InputVars

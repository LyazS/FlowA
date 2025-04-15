from app.uisdk import *

from ..UI_Components.NFlex import NFlex
from ..UI_Components.Header import Header
from ..UI_Components.NText import NText
from ..UI_Components.NButton import NButton


class UI_Drag_Branch(NormalComponent):
    def __init__(self):
        super().__init__(
            Type="VueDraggable",
            Props={
                "ghostClass": "ghost",
                "animation": 150,
                "modelValue": VModelProp(
                    Data=[
                        THIS_NODE_DATA,
                        "Connections",
                        "Outputs",
                        "Order",
                    ]
                ),
            },
            Slots={
                "default": ForLoopComponent(
                    Items=VBindProp(
                        Data=[
                            THIS_NODE_DATA,
                            "Connections",
                            "Outputs",
                            "Order",
                        ]
                    ),
                    ItemLabel="@OutHandleName",
                    IndexLabel="@OutHandleIndex",
                    Template=NFlex(
                        justify="center",
                        align="center",
                        style={
                            "width": "100%",
                            "height": "100%",
                        },
                        slots={
                            "default": [
                                SpanComponent(
                                    Type=ComponentType.VBIND,
                                    Data=[
                                        THIS_NODE_DATA,
                                        "Connections",
                                        "Outputs",
                                        "ById",
                                        "@OutHandleName",
                                        "Label",
                                    ],
                                ),
                            ]
                        },
                    ),
                )
            },
        )


class UI_Cond_Branch(NFlex):
    def __init__(self):
        super().__init__(
            vertical=True,
            slots={
                "default": [
                    NFlex(
                        vertical=False,
                        wrap=False,
                        justify="space-between",
                        style={"align-content": "center", "align-items": "center"},
                        slots={
                            "default": [
                                Header(
                                    type="warning",
                                    text=ValueProp(Data="分支设计"),
                                ),
                                NButton(
                                    type="warning",
                                    text=True,
                                    onClick=FunctionProp(Funcs=[]),
                                    slots={
                                        "default": SpanComponent(
                                            Type=ComponentType.VALUE, Data="新增分支"
                                        ),
                                        "icon": NormalComponent(Type="Add"),
                                    },
                                ),
                            ]
                        },
                    ),
                    UI_Drag_Branch(),
                ]
            },
        )


EXPORT_UI = UI_Cond_Branch

from app.schemas.VFNodeInterface import (
    VFNodeConnectionType,
    VFNodeConnectionDataType,
    VFNodeContentData,
)

from app.uisdk import *
from ..UI_Components.NFlex import NFlex
from ..UI_Components.Header import Header
from ..UI_Components.NText import NText
from ..UI_Components.NInput import NInput
from ..UI_Components.NSwitch import NSwitch
from ..UI_Components.NButton import NButton
from ..UI_Components.UI_InputVars import VarType
from ..UI_Components.RefVarSelect import UI_RefVarSelect
from .aggregate_branchs import Single_AggregateBranch, NodeAndOutHandle


class UI_Branch_Card(NFlex):
    def __init__(self):
        super().__init__()


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
                        "Payloads",
                        "ById",
                        PAYLOADS_ID,
                        "Data",
                    ]
                ),
            },
            Slots={
                "default": ForLoopComponent(
                    Items=VBindProp(
                        Data=[
                            THIS_NODE_DATA,
                            "Payloads",
                            "ById",
                            PAYLOADS_ID,
                            "Data",
                        ]
                    ),
                    ItemLabel="@BranchItem",
                    IndexLabel="@BranchIndex",
                    Template=UI_Branch_Card(),
                )
            },
        )


class UI_Aggregate_Branch(NFlex):
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
                                    text=VBindProp(
                                        Data=[
                                            THIS_NODE_DATA,
                                            "Payloads",
                                            "ById",
                                            PAYLOADS_ID,
                                            "Label",
                                        ]
                                    ),
                                ),
                                NButton(
                                    type="warning",
                                    text=True,
                                    onClick=FunctionProp(
                                        Funcs=[
                                            SETCONTEXT_FuncProp(
                                                Arg=FuncArg_SETCONTEXT(
                                                    Key=ValueProp(Data="orderkey"),
                                                    Value=VBindProp(
                                                        Data=[GENERATE_UUID]
                                                    ),
                                                )
                                            ),
                                            APPENDITEM_FuncProp(
                                                Arg=FuncArg_APPENDITEM(
                                                    DstPath=[
                                                        THIS_NODE_DATA,
                                                        "Payloads",
                                                        "ById",
                                                        PAYLOADS_ID,
                                                        "Data",
                                                    ],
                                                    ItemValue=Single_AggregateBranch(
                                                        Node=NodeAndOutHandle(
                                                            Node="",
                                                            Handle="",
                                                        ).model_dump_json(),
                                                        RefData="",
                                                        OrderKey=VBindProp(
                                                            Data=[
                                                                CONTEXT_ARG,
                                                                "orderkey",
                                                            ],
                                                            Replace="{{Data}}",
                                                        ),
                                                    ),
                                                )
                                            ),
                                        ]
                                    ),
                                    slots={
                                        "default": SpanComponent(
                                            Type=ComponentType.VALUE,
                                            Data="新增",
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


EXPORT_UI = UI_Aggregate_Branch

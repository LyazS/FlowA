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
from .aggregate_branchs import Single_AggregateBranch
from ..UI_Components.RefNodeHandleSelect import UI_RefNodeHandleSelect


class UI_Branch_Select(NFlex):
    def __init__(self):
        super().__init__(
            vertical=False,
            wrap=False,
            justify="flex-start",
            style={"align-content": "center", "align-items": "center", "width": "95%"},
            slots={
                "default": [
                    NormalComponent(
                        Type="NIcon",
                        Props={"width": "10%"},
                        Slots={"default": NormalComponent(Type="EllipsisVertical")},
                    ),
                    UI_RefNodeHandleSelect(
                        placeholder="请选择节点",
                        style={"width": "45%"},
                        value=VModelProp(
                            [
                                THIS_NODE_DATA,
                                "Payloads",
                                "ById",
                                VBindProp(
                                    [
                                        COMPONENT_CONTEXT,
                                        PAYLOADS_ID,
                                    ]
                                ),
                                "Data",
                                VBindProp([VFOR_DATA, "@BranchIndex"]),
                                "NodeHandle",
                            ]
                        ),
                        options=VBindProp(
                            [
                                CONNECT_DATA,
                                "--node",
                                CONNECT_PRE_NODE,
                                "--inhid",
                                "input",
                                "--handle",
                                VFNodeConnectionType.Outputs,
                                "--stricthid",
                                "input",
                                "--outfmt",
                                CONNECT_DATA_TO_SELECT,
                                "--level",
                                CONNECT_HANDLE_LEVEL,
                            ]
                        ),
                    ),
                    UI_RefVarSelect(
                        placeholder="请选择变量",
                        style={"width": "45%"},
                        value=VModelProp(
                            [
                                THIS_NODE_DATA,
                                "Payloads",
                                "ById",
                                VBindProp(
                                    [
                                        COMPONENT_CONTEXT,
                                        PAYLOADS_ID,
                                    ]
                                ),
                                "Data",
                                VBindProp([VFOR_DATA, "@BranchIndex"]),
                                "RefData",
                            ]
                        ),
                        options=VBindProp(
                            [
                                CONNECT_DATA,
                                "--node",
                                VBindProp(
                                    [
                                        VFOR_DATA,
                                        "@BranchItem",
                                        "NodeHandle",
                                        "Node",
                                    ]
                                ),
                                "--handle",
                                VBindProp(
                                    [
                                        VFOR_DATA,
                                        "@BranchItem",
                                        "NodeHandle",
                                        "HandleType",
                                    ]
                                ),
                                "--hid",
                                VBindProp(
                                    [VFOR_DATA, "@BranchItem", "NodeHandle", "Handle"]
                                ),
                                "--outfmt",
                                CONNECT_DATA_TO_SELECT,
                                "--level",
                                CONNECT_VAR_LEVEL,
                            ]
                        ),
                        IfCondition=CompareCondition(
                            Left=VBindProp(
                                [
                                    VFOR_DATA,
                                    "@BranchItem",
                                    "NodeHandle",
                                    "Handle",
                                ]
                            ),
                            Operator="!=",
                            Right=ValueProp(None),
                        ),
                    ),
                ]
            },
        )


class UI_Single_Branch(NFlex):
    def __init__(self):
        super().__init__(
            otherProps={"key": VBindProp([VFOR_DATA, "@BranchItem", "OrderKey"])},
            vertical=False,
            wrap=False,
            justify="flex-start",
            style={
                "align-content": "center",
                "align-items": "center",
                "margin": "10px",
            },
            slots={
                "default": [
                    UI_Branch_Select(),
                    NButton(
                        style={"width": "5%"},
                        type="error",
                        size="small",
                        circle=True,
                        level="tertiary",
                        onClick=OperateFunctionProp(
                            [
                                REMOVEITEM_FuncProp(
                                    Arg=FuncArg_REMOVEITEM(
                                        DstPath=VBindProp(
                                            [
                                                THIS_NODE_DATA,
                                                "Payloads",
                                                "ById",
                                                VBindProp(
                                                    [
                                                        COMPONENT_CONTEXT,
                                                        PAYLOADS_ID,
                                                    ]
                                                ),
                                                "Data",
                                            ]
                                        ),
                                        ItemKey=VBindProp([VFOR_DATA, "@BranchIndex"]),
                                    ),
                                )
                            ]
                        ),
                        slots={
                            "icon": NormalComponent(Type="Close"),
                        },
                    ),
                ]
            },
        )


class UI_Drag_Branch(NormalComponent):
    def __init__(self):
        super().__init__(
            Type="VueDraggable",
            Props={
                "ghostClass": "ghost",
                "animation": 150,
                "modelValue": VModelProp(
                    [
                        THIS_NODE_DATA,
                        "Payloads",
                        "ById",
                        VBindProp(
                            [
                                COMPONENT_CONTEXT,
                                PAYLOADS_ID,
                            ]
                        ),
                        "Data",
                    ]
                ),
            },
            Slots={
                "default": ForLoopComponent(
                    Items=VBindProp(
                        [
                            THIS_NODE_DATA,
                            "Payloads",
                            "ById",
                            VBindProp(
                                [
                                    COMPONENT_CONTEXT,
                                    PAYLOADS_ID,
                                ]
                            ),
                            "Data",
                        ]
                    ),
                    ItemLabel="@BranchItem",
                    IndexLabel="@BranchIndex",
                    Template=UI_Single_Branch(),
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
                                        [
                                            THIS_NODE_DATA,
                                            "Payloads",
                                            "ById",
                                            VBindProp(
                                                [
                                                    COMPONENT_CONTEXT,
                                                    PAYLOADS_ID,
                                                ]
                                            ),
                                            "Label",
                                        ]
                                    ),
                                ),
                                NButton(
                                    type="warning",
                                    text=True,
                                    onClick=OperateFunctionProp(
                                        [
                                            SETCONTEXT_FuncProp(
                                                Arg=FuncArg_SETCONTEXT(
                                                    Key=ValueProp("orderkey"),
                                                    Value=ReturnFunctionProp(
                                                        GENERATEUUID_FuncProp()
                                                    ),
                                                    # VBindProp([GENERATE_UUID]),
                                                )
                                            ),
                                            APPENDITEM_FuncProp(
                                                Arg=FuncArg_APPENDITEM(
                                                    DstPath=VBindProp(
                                                        [
                                                            THIS_NODE_DATA,
                                                            "Payloads",
                                                            "ById",
                                                            VBindProp(
                                                                [
                                                                    COMPONENT_CONTEXT,
                                                                    PAYLOADS_ID,
                                                                ]
                                                            ),
                                                            "Data",
                                                        ]
                                                    ),
                                                    ItemValue=Single_AggregateBranch(
                                                        OrderKey=VBindProp(
                                                            [
                                                                ARG_CONTEXT,
                                                                "orderkey",
                                                            ]
                                                        )
                                                    ),
                                                )
                                            ),
                                        ]
                                    ),
                                    slots={
                                        "default": SpanComponent(ValueProp("新增")),
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

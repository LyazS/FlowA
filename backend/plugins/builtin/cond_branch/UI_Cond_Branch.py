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
from .cond_branch import (
    Single_Condition,
    Single_ConditionDict,
    LengthTypeSelections,
    StartEndTypeSelections,
    NullTypeSelections,
    EqualTypeSelections,
    NotEqualTypeSelections,
    ContainsTypeSelections,
)


class branch_header(NFlex):
    def __init__(self):
        super().__init__(
            vertical=False,
            wrap=False,
            justify="flex-start",
            style={"align-content": "center", "align-items": "center"},
            slots={
                "default": [
                    NormalComponent(
                        Type="NIcon",
                        Props={},
                        Slots={"default": NormalComponent(Type="EllipsisVertical")},
                    ),
                    NormalComponent(
                        Type="NSwitch",
                        Props={
                            "size": "small",
                            "style": {"width": "12em"},
                            "value": VModelProp(
                                [
                                    THIS_NODE_DATA,
                                    "Payloads",
                                    "ById",
                                    VBindProp([VFOR_DATA, "@OutHandleName"]),
                                    "Data",
                                    "CondIsAnd",
                                ]
                            ),
                        },
                        Slots={
                            "checked": SpanComponent(ValueProp("AND")),
                            "unchecked": SpanComponent(ValueProp("OR")),
                        },
                    ),
                    NormalComponent(
                        Type="NInputGroup",
                        Props={},
                        Slots={
                            "default": [
                                NormalComponent(
                                    Type="NTag",
                                    Props={
                                        "bordered": False,
                                        "type": "info",
                                        "size": "small",
                                        "round": True,
                                    },
                                    Slots={"default": SpanComponent(ValueProp("•"))},
                                ),
                                NormalComponent(
                                    Type="NInput",
                                    Props={
                                        "size": "tiny",
                                        "autosize": True,
                                        "style": {
                                            "min-width": "20%",
                                        },
                                        "placeholder": "分支名",
                                        "value": VModelProp(
                                            [
                                                THIS_NODE_DATA,
                                                "Connections",
                                                "Outputs",
                                                "ById",
                                                VBindProp(
                                                    [VFOR_DATA, "@OutHandleName"]
                                                ),
                                                "Label",
                                            ]
                                        ),
                                    },
                                ),
                            ]
                        },
                    ),
                ]
            },
        )


class VarTypeSelect(NormalComponent):
    def __init__(self):
        super().__init__(
            Type="NSelect",
            Props={
                "style": {"width": "20%"},
                "size": "small",
                "consistent-menu-width": False,
                "options": [
                    {"label": "引用", "value": VarType.Ref},
                    {"label": "字符串", "value": VarType.String},
                    {"label": "整数", "value": VarType.Integer},
                    {"label": "数字", "value": VarType.Number},
                    {"label": "布尔", "value": VarType.Boolean},
                ],
                "value": VModelProp(
                    [
                        THIS_NODE_DATA,
                        "Payloads",
                        "ById",
                        VBindProp([VFOR_DATA, "@OutHandleName"]),
                        "Data",
                        "Conditions",
                        VBindProp([VFOR_DATA, "@CondIndex"]),
                        "CompareType",
                    ]
                ),
            },
        )


class VarStringInput(NInput):
    def __init__(self):
        super().__init__(
            size="small",
            style={"width": "80%"},
            value=VModelProp(
                [
                    THIS_NODE_DATA,
                    "Payloads",
                    "ById",
                    VBindProp([VFOR_DATA, "@OutHandleName"]),
                    "Data",
                    "Conditions",
                    VBindProp([VFOR_DATA, "@CondIndex"]),
                    "ValueStr",
                ],
            ),
            IfCondition=CompareCondition(
                Left=VBindProp(
                    [
                        THIS_NODE_DATA,
                        "Payloads",
                        "ById",
                        VBindProp([VFOR_DATA, "@OutHandleName"]),
                        "Data",
                        "Conditions",
                        VBindProp([VFOR_DATA, "@CondIndex"]),
                        "CompareType",
                    ]
                ),
                Operator="==",
                Right=ValueProp(VarType.String),
            ),
        )


class VarIntegerInput(NormalComponent):
    def __init__(self):
        super().__init__(
            Type="NInputNumber",
            Props={
                "size": "small",
                "style": {"width": "80%"},
                "value": VModelProp(
                    [
                        THIS_NODE_DATA,
                        "Payloads",
                        "ById",
                        VBindProp([VFOR_DATA, "@OutHandleName"]),
                        "Data",
                        "Conditions",
                        VBindProp([VFOR_DATA, "@CondIndex"]),
                        "ValueNum",
                    ],
                ),
                "precision": 0,
            },
            IfCondition=CompareCondition(
                Left=VBindProp(
                    [
                        THIS_NODE_DATA,
                        "Payloads",
                        "ById",
                        VBindProp([VFOR_DATA, "@OutHandleName"]),
                        "Data",
                        "Conditions",
                        VBindProp([VFOR_DATA, "@CondIndex"]),
                        "CompareType",
                    ]
                ),
                Operator="==",
                Right=ValueProp(VarType.Integer),
            ),
        )


class VarNumberInput(NormalComponent):
    def __init__(self):
        super().__init__(
            Type="NInputNumber",
            Props={
                "size": "small",
                "style": {"width": "80%"},
                "value": VModelProp(
                    [
                        THIS_NODE_DATA,
                        "Payloads",
                        "ById",
                        VBindProp([VFOR_DATA, "@OutHandleName"]),
                        "Data",
                        "Conditions",
                        VBindProp([VFOR_DATA, "@CondIndex"]),
                        "ValueNum",
                    ],
                ),
            },
            IfCondition=CompareCondition(
                Left=VBindProp(
                    [
                        THIS_NODE_DATA,
                        "Payloads",
                        "ById",
                        VBindProp([VFOR_DATA, "@OutHandleName"]),
                        "Data",
                        "Conditions",
                        VBindProp([VFOR_DATA, "@CondIndex"]),
                        "CompareType",
                    ]
                ),
                Operator="==",
                Right=ValueProp(VarType.Number),
            ),
        )


class VarBooleanInput(NFlex):
    def __init__(self):
        super().__init__(
            justify="start",
            style={"width": "50%"},
            slots={
                "default": NSwitch(
                    size="medium",
                    style={"width": "50%"},
                    value=VModelProp(
                        [
                            THIS_NODE_DATA,
                            "Payloads",
                            "ById",
                            VBindProp([VFOR_DATA, "@OutHandleName"]),
                            "Data",
                            "Conditions",
                            VBindProp([VFOR_DATA, "@CondIndex"]),
                            "ValueBool",
                        ],
                    ),
                )
            },
            IfCondition=CompareCondition(
                Left=VBindProp(
                    [
                        THIS_NODE_DATA,
                        "Payloads",
                        "ById",
                        VBindProp([VFOR_DATA, "@OutHandleName"]),
                        "Data",
                        "Conditions",
                        VBindProp([VFOR_DATA, "@CondIndex"]),
                        "CompareType",
                    ]
                ),
                Operator="==",
                Right=ValueProp(VarType.Boolean),
            ),
        )

    pass


class UI_Cond_Card_Content(NFlex):
    def __init__(self):
        super().__init__(
            vertical=True,
            slots={
                "default": [
                    NFlex(
                        vertical=False,
                        wrap=False,
                        justify="flex-start",
                        style={
                            "align-content": "center",
                            "align-items": "center",
                        },
                        slots={
                            "default": [
                                UI_RefVarSelect(
                                    style={"width": "65%"},
                                    size="small",
                                    value=VModelProp(
                                        [
                                            THIS_NODE_DATA,
                                            "Payloads",
                                            "ById",
                                            VBindProp([VFOR_DATA, "@OutHandleName"]),
                                            "Data",
                                            "Conditions",
                                            VBindProp([VFOR_DATA, "@CondIndex"]),
                                            "Refdata",
                                        ]
                                    ),
                                    options=VBindProp(
                                        [
                                            CONNECT_DATA,
                                            "--node",
                                            CONNECT_CUR_NODE,
                                            "--handle",
                                            VFNodeConnectionType.Self,
                                            "--hid",
                                            "self",
                                            "--outfmt",
                                            CONNECT_DATA_TO_SELECT,
                                            "--level",
                                            CONNECT_VAR_LEVEL,
                                        ]
                                    ),
                                ),
                                NormalComponent(
                                    Type="NSelect",
                                    Props={
                                        "size": "small",
                                        "style": {"width": "35%"},
                                        "consistent-menu-width": False,
                                        "options": []
                                        + EqualTypeSelections
                                        + NotEqualTypeSelections
                                        + StartEndTypeSelections
                                        + LengthTypeSelections
                                        + ContainsTypeSelections
                                        + NullTypeSelections
                                        + [],
                                        "value": VModelProp(
                                            [
                                                THIS_NODE_DATA,
                                                "Payloads",
                                                "ById",
                                                VBindProp(
                                                    [VFOR_DATA, "@OutHandleName"]
                                                ),
                                                "Data",
                                                "Conditions",
                                                VBindProp([VFOR_DATA, "@CondIndex"]),
                                                "Operator",
                                            ]
                                        ),
                                    },
                                ),
                            ]
                        },
                    ),
                    NFlex(
                        vertical=False,
                        wrap=False,
                        justify="flex-start",
                        style={
                            "align-content": "center",
                            "align-items": "center",
                        },
                        slots={
                            "default": [
                                VarTypeSelect(),
                                VarStringInput(),
                                VarIntegerInput(),
                                VarNumberInput(),
                                VarBooleanInput(),
                                UI_RefVarSelect(
                                    size="small",
                                    style={"width": "80%"},
                                    options=VBindProp(
                                        [
                                            CONNECT_DATA,
                                            "--node",
                                            CONNECT_CUR_NODE,
                                            "--handle",
                                            VFNodeConnectionType.Self,
                                            "--hid",
                                            "self",
                                            "--outfmt",
                                            CONNECT_DATA_TO_SELECT,
                                            "--level",
                                            CONNECT_VAR_LEVEL,
                                        ]
                                    ),
                                    value=VModelProp(
                                        [
                                            THIS_NODE_DATA,
                                            "Payloads",
                                            "ById",
                                            VBindProp([VFOR_DATA, "@OutHandleName"]),
                                            "Data",
                                            "Conditions",
                                            VBindProp([VFOR_DATA, "@CondIndex"]),
                                            "ValueRef",
                                        ],
                                    ),
                                    IfCondition=CompareCondition(
                                        Left=VBindProp(
                                            [
                                                THIS_NODE_DATA,
                                                "Payloads",
                                                "ById",
                                                VBindProp(
                                                    [VFOR_DATA, "@OutHandleName"]
                                                ),
                                                "Data",
                                                "Conditions",
                                                VBindProp([VFOR_DATA, "@CondIndex"]),
                                                "CompareType",
                                            ]
                                        ),
                                        Operator="==",
                                        Right=ValueProp(VarType.Ref),
                                    ),
                                ),
                            ]
                        },
                    ),
                ]
            },
        )


class UI_Cond_Card(NFlex):
    def __init__(self):
        super().__init__(
            vertical=False,
            wrap=False,
            justify="flex-start",
            style={"align-content": "center", "align-items": "center"},
            slots={
                "default": [
                    NormalComponent(
                        Type="NCard",
                        Props={
                            "style": {"width": "95%"},
                            "bordered": True,
                            "hoverable": True,
                            "size": "small",
                        },
                        Slots={
                            "default": UI_Cond_Card_Content(),
                        },
                    ),
                    NButton(
                        style={"width": "5%"},
                        type="error",
                        size="small",
                        circle=True,
                        level="tertiary",
                        onClick=FunctionProp(
                            Funcs=[
                                REMOVEITEM_FuncProp(
                                    Arg=FuncArg_REMOVEITEM(
                                        DstPath=VBindProp(
                                            [
                                                THIS_NODE_DATA,
                                                "Payloads",
                                                "ById",
                                                VBindProp(
                                                    [VFOR_DATA, "@OutHandleName"]
                                                ),
                                                "Data",
                                                "Conditions",
                                            ]
                                        ),
                                        ItemKey=VBindProp([VFOR_DATA, "@CondIndex"]),
                                    )
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


class UI_Branch_Card(NormalComponent):
    def __init__(self):
        super().__init__(
            Type="NCard",
            Props={
                "key": VBindProp([VFOR_DATA, "@OutHandleName"]),
                "bordered": True,
                "hoverable": True,
                "size": "small",
                "style": {"margin-bottom": "5px"},
            },
            Slots={
                "header": branch_header(),
                "header-extra": NButton(
                    type="error",
                    text=True,
                    onClick=FunctionProp(
                        Funcs=[
                            REMOVEPAYLOAD_FuncProp(
                                Arg=FuncArg_REMOVEPAYLOAD(
                                    PayloadId=VBindProp([VFOR_DATA, "@OutHandleName"]),
                                )
                            ),
                            REMOVEHANDLE_FuncProp(
                                Arg=FuncArg_REMOVEHANDLE(
                                    HandleType=VFNodeConnectionType.Outputs,
                                    HandleId=VBindProp([VFOR_DATA, "@OutHandleName"]),
                                )
                            ),
                        ]
                    ),
                    slots={
                        "default": SpanComponent(ValueProp("删除分支")),
                        "icon": NormalComponent(Type="Close"),
                    },
                ),
                "default": NFlex(
                    vertical=True,
                    slots={
                        "default": [
                            ForLoopComponent(
                                Items=VBindProp(
                                    [
                                        THIS_NODE_DATA,
                                        "Payloads",
                                        "ById",
                                        VBindProp([VFOR_DATA, "@OutHandleName"]),
                                        "Data",
                                        "Conditions",
                                    ]
                                ),
                                ItemLabel="@CondItem",
                                IndexLabel="@CondIndex",
                                Template=UI_Cond_Card(),
                            ),
                            NButton(
                                style={"width": "100%"},
                                type="success",
                                text=True,
                                onClick=FunctionProp(
                                    Funcs=[
                                        APPENDITEM_FuncProp(
                                            Arg=FuncArg_APPENDITEM(
                                                DstPath=VBindProp(
                                                    [
                                                        THIS_NODE_DATA,
                                                        "Payloads",
                                                        "ById",
                                                        VBindProp(
                                                            [
                                                                VFOR_DATA,
                                                                "@OutHandleName",
                                                            ]
                                                        ),
                                                        "Data",
                                                        "Conditions",
                                                    ]
                                                ),
                                                ItemValue=Single_Condition(),
                                            )
                                        )
                                    ]
                                ),
                                slots={
                                    "default": SpanComponent(ValueProp("添加条件")),
                                    "icon": NormalComponent(Type="Add"),
                                },
                            ),
                        ]
                    },
                ),
            },
            IfCondition=CompareCondition(
                Left=VBindProp([VFOR_DATA, "@OutHandleName"]),
                Operator="!=",
                Right=ValueProp("output-else"),
            ),
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
                        "Connections",
                        "Outputs",
                        "Order",
                    ]
                ),
                "onUpdate": FunctionProp(
                    Funcs=[
                        UPDATENODEINTERNAL_FuncProp(),
                    ]
                ),
            },
            Slots={
                "default": ForLoopComponent(
                    Items=VBindProp(
                        [
                            THIS_NODE_DATA,
                            "Connections",
                            "Outputs",
                            "Order",
                        ]
                    ),
                    ItemLabel="@OutHandleName",
                    IndexLabel="@OutHandleIndex",
                    Template=UI_Branch_Card(),
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
                                    text=ValueProp("分支设计"),
                                ),
                                NButton(
                                    type="warning",
                                    text=True,
                                    onClick=FunctionProp(
                                        Funcs=[
                                            SETCONTEXT_FuncProp(
                                                Arg=FuncArg_SETCONTEXT(
                                                    Key=ValueProp("branchid"),
                                                    Value=VBindProp(
                                                        [GENERATE_UUID],
                                                        Replace="output-{{Data}}",  # handle必须以output|input开头
                                                    ),
                                                )
                                            ),
                                            ADDHANDLE_FuncProp(
                                                Arg=FuncArg_ADDHANDLE(
                                                    HandleType=VFNodeConnectionType.Outputs,
                                                    HandleId=VBindProp(
                                                        [
                                                            CONTEXT_ARG,
                                                            "branchid",
                                                        ],
                                                    ),
                                                    HandleLabel=ValueProp("CASE X"),
                                                    Position=InsertPos.Start,
                                                )
                                            ),
                                            ADDHANDLEDATA_FuncProp(
                                                Arg=FuncArg_ADDHANDLEDATA(
                                                    HandleType=VFNodeConnectionType.Outputs,
                                                    HandleId=VBindProp(
                                                        [
                                                            CONTEXT_ARG,
                                                            "branchid",
                                                        ],
                                                    ),
                                                    Data=VFNodeHandleData(
                                                        Type=VFNodeConnectionDataType.FromOuter,
                                                        HandleId="input-var",
                                                    ),
                                                )
                                            ),
                                            ADDPAYLOAD_FuncProp(
                                                Arg=FuncArg_ADDPAYLOAD(
                                                    PayloadId=VBindProp(
                                                        [
                                                            CONTEXT_ARG,
                                                            "branchid",
                                                        ],
                                                    ),
                                                    Payload=VFNodeContentData(
                                                        Label="-",
                                                        Type=VarType.Dict,
                                                        Data=Single_ConditionDict(
                                                            OutputKey=VBindProp(
                                                                [
                                                                    CONTEXT_ARG,
                                                                    "branchid",
                                                                ],
                                                            ),
                                                            CondIsAnd=True,
                                                            Conditions=[
                                                                Single_Condition()
                                                            ],
                                                        ),
                                                    ),
                                                )
                                            ),
                                        ]
                                    ),
                                    slots={
                                        "default": SpanComponent(ValueProp("新增分支")),
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

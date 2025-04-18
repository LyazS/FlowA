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
                                Data=[
                                    THIS_NODE_DATA,
                                    "Results",
                                    "ById",
                                    "@OutHandleName",
                                    "Data",
                                    "CondIsAnd",
                                ]
                            ),
                        },
                        Slots={
                            "checked": SpanComponent(
                                Type=ComponentType.VALUE,
                                Data="AND",
                            ),
                            "unchecked": SpanComponent(
                                Type=ComponentType.VALUE,
                                Data="OR",
                            ),
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
                                    Slots={
                                        "default": SpanComponent(
                                            Type=ComponentType.VALUE,
                                            Data="•",
                                        )
                                    },
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
                                            Data=[
                                                THIS_NODE_DATA,
                                                "Connections",
                                                "Outputs",
                                                "ById",
                                                "@OutHandleName",
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
                    Data=[
                        THIS_NODE_DATA,
                        "Results",
                        "ById",
                        "@OutHandleName",
                        "Data",
                        "Conditions",
                        "@CondIndex",
                        "Comparetype",
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
                Data=[
                    THIS_NODE_DATA,
                    "Results",
                    "ById",
                    "@OutHandleName",
                    "Data",
                    "Conditions",
                    "@CondIndex",
                    "valueStr",
                ],
            ),
            IfCondition=CompareCondition(
                Left=VBindProp(
                    Data=[
                        THIS_NODE_DATA,
                        "Results",
                        "ById",
                        "@OutHandleName",
                        "Data",
                        "Conditions",
                        "@CondIndex",
                        "CompareType",
                    ]
                ),
                Operator="==",
                Right=ValueProp(Data=VarType.String),
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
                    Data=[
                        THIS_NODE_DATA,
                        "Results",
                        "ById",
                        "@OutHandleName",
                        "Data",
                        "Conditions",
                        "@CondIndex",
                        "valueNum",
                    ],
                ),
                "precision": 0,
            },
            IfCondition=CompareCondition(
                Left=VBindProp(
                    Data=[
                        THIS_NODE_DATA,
                        "Results",
                        "ById",
                        "@OutHandleName",
                        "Data",
                        "Conditions",
                        "@CondIndex",
                        "CompareType",
                    ]
                ),
                Operator="==",
                Right=ValueProp(Data=VarType.Integer),
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
                    Data=[
                        THIS_NODE_DATA,
                        "Results",
                        "ById",
                        "@OutHandleName",
                        "Data",
                        "Conditions",
                        "@CondIndex",
                        "valueNum",
                    ],
                ),
            },
            IfCondition=CompareCondition(
                Left=VBindProp(
                    Data=[
                        THIS_NODE_DATA,
                        "Results",
                        "ById",
                        "@OutHandleName",
                        "Data",
                        "Conditions",
                        "@CondIndex",
                        "CompareType",
                    ]
                ),
                Operator="==",
                Right=ValueProp(Data=VarType.Number),
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
                        Data=[
                            THIS_NODE_DATA,
                            "Results",
                            "ById",
                            "@OutHandleName",
                            "Data",
                            "Conditions",
                            "@CondIndex",
                            "valueBool",
                        ],
                    ),
                )
            },
            IfCondition=CompareCondition(
                Left=VBindProp(
                    Data=[
                        THIS_NODE_DATA,
                        "Results",
                        "ById",
                        "@OutHandleName",
                        "Data",
                        "Conditions",
                        "@CondIndex",
                        "CompareType",
                    ]
                ),
                Operator="==",
                Right=ValueProp(Data=VarType.Boolean),
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
                                        Data=[
                                            THIS_NODE_DATA,
                                            "Results",
                                            "ById",
                                            "@OutHandleName",
                                            "Data",
                                            "Conditions",
                                            "@CondIndex",
                                            "Refdata",
                                        ]
                                    ),
                                    options=VBindProp(
                                        Data=[
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
                                            Data=[
                                                THIS_NODE_DATA,
                                                "Results",
                                                "ById",
                                                "@OutHandleName",
                                                "Data",
                                                "Conditions",
                                                "@CondIndex",
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
                                        Data=[
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
                                        Data=[
                                            THIS_NODE_DATA,
                                            "Results",
                                            "ById",
                                            "@OutHandleName",
                                            "Data",
                                            "Conditions",
                                            "@CondIndex",
                                            "valueStr",
                                        ],
                                    ),
                                    IfCondition=CompareCondition(
                                        Left=VBindProp(
                                            Data=[
                                                THIS_NODE_DATA,
                                                "Results",
                                                "ById",
                                                "@OutHandleName",
                                                "Data",
                                                "Conditions",
                                                "@CondIndex",
                                                "CompareType",
                                            ]
                                        ),
                                        Operator="==",
                                        Right=ValueProp(Data=VarType.Ref),
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
                                        DstPath=[
                                            THIS_NODE_DATA,
                                            "Results",
                                            "ById",
                                            "@OutHandleName",
                                            "Data",
                                            "Conditions",
                                        ],
                                        ItemKey=VBindProp(
                                            Data=[VFOR_DATA, "@CondIndex"]
                                        ),
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
                "key": VBindProp(Data=[VFOR_DATA, "@OutHandleName"]),
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
                            REMOVERESULT_FuncProp(
                                Arg=FuncArg_REMOVERESULT(
                                    ResultId=VBindProp(
                                        Data=[VFOR_DATA, "@OutHandleName"]
                                    ),
                                )
                            ),
                            REMOVEHANDLE_FuncProp(
                                Arg=FuncArg_REMOVEHANDLE(
                                    HandleType=VFNodeConnectionType.Outputs,
                                    HandleId=VBindProp(
                                        Data=[VFOR_DATA, "@OutHandleName"]
                                    ),
                                )
                            ),
                        ]
                    ),
                    slots={
                        "default": SpanComponent(
                            Type=ComponentType.VALUE, Data="删除分支"
                        ),
                        "icon": NormalComponent(Type="Close"),
                    },
                ),
                "default": NFlex(
                    vertical=True,
                    slots={
                        "default": [
                            ForLoopComponent(
                                Items=VBindProp(
                                    Data=[
                                        THIS_NODE_DATA,
                                        "Results",
                                        "ById",
                                        "@OutHandleName",
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
                                                DstPath=[
                                                    THIS_NODE_DATA,
                                                    "Results",
                                                    "ById",
                                                    "@OutHandleName",
                                                    "Data",
                                                    "Conditions",
                                                ],
                                                ItemValue=Single_Condition(
                                                    Refdata="",
                                                    Operator="eq",
                                                    CompareType=VarType.Ref,
                                                    valueStr="",
                                                    valueNum=0,
                                                    valueBool=False,
                                                ),
                                            )
                                        )
                                    ]
                                ),
                                slots={
                                    "default": SpanComponent(
                                        Type=ComponentType.VALUE,
                                        Data="添加条件",
                                    ),
                                    "icon": NormalComponent(Type="Add"),
                                },
                            ),
                        ]
                    },
                ),
            },
            IfCondition=CompareCondition(
                Left=VBindProp(Data=[VFOR_DATA, "@OutHandleName"]),
                Operator="!=",
                Right=ValueProp(Data="output-else"),
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
                    Data=[
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
                        Data=[
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
                                    text=ValueProp(Data="分支设计"),
                                ),
                                NButton(
                                    type="warning",
                                    text=True,
                                    onClick=FunctionProp(
                                        Funcs=[
                                            SETCONTEXT_FuncProp(
                                                Arg=FuncArg_SETCONTEXT(
                                                    Key=ValueProp(Data="bid"),
                                                    Value=VBindProp(
                                                        Data=[GENERATE_UUID]
                                                    ),
                                                )
                                            ),
                                            ADDHANDLE_FuncProp(
                                                Arg=FuncArg_ADDHANDLE(
                                                    HandleType=VFNodeConnectionType.Outputs,
                                                    HandleId=VBindProp(
                                                        Data=[
                                                            CONTEXT_ARG,
                                                            "bid",
                                                        ],
                                                        Replace="output-{{Data}}",  # handle必须以output|input开头
                                                    ),
                                                    HandleLabel=ValueProp(
                                                        Data="CASE X"
                                                    ),
                                                    Position=InsertPos.Start,
                                                )
                                            ),
                                            ADDHANDLEDATA_FuncProp(
                                                Arg=FuncArg_ADDHANDLEDATA(
                                                    HandleType=VFNodeConnectionType.Outputs,
                                                    HandleId=VBindProp(
                                                        Data=[
                                                            CONTEXT_ARG,
                                                            "bid",
                                                        ],
                                                        Replace="output-{{Data}}",
                                                    ),
                                                    Data=VFNodeHandleData(
                                                        Type=VFNodeConnectionDataType.FromOuter,
                                                        HandleId="input-var",
                                                    ),
                                                )
                                            ),
                                            ADDRESULT_FuncProp(
                                                Arg=FuncArg_ADDRESULT(
                                                    ResultId=VBindProp(
                                                        Data=[
                                                            CONTEXT_ARG,
                                                            "bid",
                                                        ],
                                                        Replace="output-{{Data}}",
                                                    ),
                                                    Result=VFNodeContentData(
                                                        Label="-",
                                                        Type="Dict",
                                                        Data=Single_ConditionDict(
                                                            OutputKey=VBindProp(
                                                                Data=[
                                                                    CONTEXT_ARG,
                                                                    "bid",
                                                                ],
                                                                Replace="output-{{Data}}",
                                                            ),
                                                            CondIsAnd=True,
                                                            Conditions=[
                                                                Single_Condition(
                                                                    Refdata="",
                                                                    Operator="eq",
                                                                    CompareType=VarType.Ref,
                                                                    valueStr="",
                                                                    valueNum=0,
                                                                    valueBool=False,
                                                                )
                                                            ],
                                                        ),
                                                    ),
                                                )
                                            ),
                                        ]
                                    ),
                                    slots={
                                        "default": SpanComponent(
                                            Type=ComponentType.VALUE,
                                            Data="新增分支",
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

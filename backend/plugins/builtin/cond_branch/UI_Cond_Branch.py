from app.schemas.VFNodeInterface import (
    VFNodeConnectionType,
    VFNodeConnectionDataType,
    VFNodeContentData,
)

from app.uisdk import *
from ..UI_Components.NFlex import NFlex
from ..UI_Components.Header import Header
from ..UI_Components.NText import NText
from ..UI_Components.NButton import NButton
from .cond_branch import ConditionType, Single_Condition, Single_ConditionDict
from ..UI_Components.UI_InputVars import VarType


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
                                            Data="分支名",
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
                        Slots={},
                    ),
                    NButton(
                        style={"width": "5%"},
                        type="error",
                        size="small",
                        circle=True,
                        level="tertiary",
                        onClick=FunctionProp(Funcs=[]),
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
                    onClick=FunctionProp(Funcs=[]),
                    slots={
                        "default": SpanComponent(
                            Type=ComponentType.VALUE, Data="删除分支"
                        ),
                        "icon": NormalComponent(Type="Close"),
                    },
                ),
                "default": UI_Cond_Card(),
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
                                                        Data="分支【请修改名字】"
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
                                                    HandleId=VBindProp(
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
                                                            outputKey=VBindProp(
                                                                Data=[
                                                                    CONTEXT_ARG,
                                                                    "bid",
                                                                ],
                                                                Replace="output-{{Data}}",
                                                            ),
                                                            condType=ConditionType.AND,
                                                            conditions=[
                                                                Single_Condition(
                                                                    refdata="",
                                                                    operator="==",
                                                                    comparetype=VarType.Ref,
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

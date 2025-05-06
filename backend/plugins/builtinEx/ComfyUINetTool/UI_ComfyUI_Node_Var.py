from typing import Optional, Dict, List, Union, Literal
from app.uisdk import *
from app.schemas.VFNodeInterface import VarType
from plugins.builtin.UI_Components.NFlex import NFlex
from plugins.builtin.UI_Components.NInput import NInput, NInputAutoSize
from plugins.builtin.UI_Components.NButton import NButton
from plugins.builtin.UI_Components.Header import Header
from plugins.builtin.UI_Components.RefVarSelect import UI_RefVarSelect
from plugins.builtin.UI_Components.UI_FileUpload import UI_FileUpload
from .ComfyUINetTool import CF_NodeVar


class UI_Card_Node_Var(NormalComponent):
    def __init__(self):
        super().__init__(
            Type="NCard",
            Props={
                "bordered": True,
                "hoverable": True,
                "size": "small",
                "style": {
                    "width": "100%",
                },
            },
            Slots={
                "default": NFlex(
                    vertical=True,
                    slots={
                        "default": [
                            NFlex(
                                vertical=False,
                                wrap=False,
                                justify="space-between",
                                style={
                                    "align-content": "center",
                                    "align-items": "center",
                                },
                                slots={
                                    "default": [
                                        NInput(
                                            size="small",
                                            placeholder="节点ID",
                                            style={"width": "20%"},
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
                                                    VBindProp([VFOR_DATA, "@Index"]),
                                                    "NodeId",
                                                ]
                                            ),
                                        ),
                                        NInput(
                                            size="small",
                                            style={"width": "50%"},
                                            placeholder="字段名",
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
                                                    VBindProp([VFOR_DATA, "@Index"]),
                                                    "FieldName",
                                                ]
                                            ),
                                        ),
                                        NormalComponent(
                                            Type="NSelect",
                                            Props={
                                                "size": "small",
                                                "style": {"width": "30%"},
                                                "value": VModelProp(
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
                                                        VBindProp(
                                                            [VFOR_DATA, "@Index"]
                                                        ),
                                                        "FieldType",
                                                    ]
                                                ),
                                                "options": [
                                                    {
                                                        "label": "字符串",
                                                        "value": VarType.String,
                                                    },
                                                    {
                                                        "label": "引用",
                                                        "value": VarType.Ref,
                                                    },
                                                ],
                                            },
                                        ),
                                    ]
                                },
                            ),
                            NInput(
                                type="textarea",
                                placeholder="字段具体值",
                                autosize=NInputAutoSize(minRows=1, maxRows=10),
                                clearable=True,
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
                                        VBindProp([VFOR_DATA, "@Index"]),
                                        "FieldValueStr",
                                    ]
                                ),
                                IfCondition=CompareCondition(
                                    Left=VBindProp(
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
                                            VBindProp([VFOR_DATA, "@Index"]),
                                            "FieldType",
                                        ]
                                    ),
                                    Operator="==",
                                    Right=ValueProp(VarType.String),
                                ),
                            ),
                            UI_RefVarSelect(
                                size="medium",
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
                                        VBindProp([VFOR_DATA, "@Index"]),
                                        "FieldValueRef",
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
                                        "--filtertypes",
                                        VarType.String,
                                    ]
                                ),
                                IfCondition=CompareCondition(
                                    Left=VBindProp(
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
                                            VBindProp([VFOR_DATA, "@Index"]),
                                            "FieldType",
                                        ]
                                    ),
                                    Operator="==",
                                    Right=ValueProp(VarType.Ref),
                                ),
                            ),
                        ]
                    },
                )
            },
        )

    pass


class UI_CF_Node_Var(NFlex):
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
                                    type="success",
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
                                                    ItemValue=CF_NodeVar(),
                                                )
                                            )
                                        ]
                                    ),
                                    slots={
                                        "default": SpanComponent(ValueProp("添加")),
                                        "icon": NormalComponent(Type="Add"),
                                    },
                                ),
                            ]
                        },
                    ),
                    ForLoopComponent(
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
                        ItemLabel="@Item",
                        IndexLabel="@Index",
                        Template=NFlex(
                            vertical=False,
                            wrap=False,
                            justify="space-between",
                            style={"align-content": "center", "align-items": "center"},
                            slots={
                                "default": [
                                    UI_Card_Node_Var(),
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
                                                        ItemKey=VBindProp(
                                                            [VFOR_DATA, "@Index"]
                                                        ),
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
                        ),
                    ),
                ]
            },
        )


EXPORT_UI = UI_CF_Node_Var

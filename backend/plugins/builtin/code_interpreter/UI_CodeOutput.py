from app.schemas.VFNodeInterface import VFNodeContentData, VarType
from app.uisdk import *
from ..UI_Components.Header import Header
from ..UI_Components.NInput import NInput
from ..UI_Components.NButton import NButton
from ..UI_Components.NFlex import NFlex


class VarNameInput(NInput):
    def __init__(self):
        super().__init__(
            style={"width": "50%"},
            size="small",
            value=VModelProp(
                [
                    THIS_NODE_DATA,
                    "Results",
                    "ById",
                    VBindProp([VFOR_DATA, "@RID"]),
                    "Label",
                ]
            ),
        )


class VarTypeSelect(NormalComponent):
    def __init__(self):
        super().__init__(
            Type="NSelect",
            Props={
                "style": {"width": "50%"},
                "size": "small",
                "consistent-menu-width": False,
                "options": [
                    {"label": "字符串 String", "value": VarType.String},
                    {"label": "整数 Integer", "value": VarType.Integer},
                    {"label": "数字 Number", "value": VarType.Number},
                    {"label": "布尔 Boolean", "value": VarType.Boolean},
                    {"label": "列表 List", "value": VarType.List},
                    {"label": "字典 Dict", "value": VarType.Dict},
                    {"label": "图片 Image", "value": VarType.Image},
                    {"label": "文件 File", "value": VarType.File},
                    {"label": "任意 Any", "value": VarType.Any},
                ],
                "value": VModelProp(
                    [
                        THIS_NODE_DATA,
                        "Results",
                        "ById",
                        VBindProp([VFOR_DATA, "@RID"]),
                        "Type",
                    ]
                ),
            },
        )


class UI_CodeOutput(NFlex):
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
                                Header(type="info", text="输出变量"),
                                NButton(
                                    type="info",
                                    text=True,
                                    onClick=OperateFunctionProp(
                                        [
                                            ADDRESULT2OUT_FuncProp(
                                                Arg=FuncArg_ADDRESULT2OUT(
                                                    HandleId=ValueProp("output"),
                                                    Result=VFNodeContentData(
                                                        Label="",
                                                        Type=VarType.String,
                                                        Data=None,
                                                    ),
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
                                "Results",
                                "Order",
                            ]
                        ),
                        ItemLabel="@RID",
                        IndexLabel="@Index",
                        Template=NFlex(
                            vertical=False,
                            wrap=False,
                            justify="space-between",
                            style={"align-content": "center", "align-items": "center"},
                            slots={
                                "default": [
                                    NFlex(
                                        vertical=False,
                                        wrap=False,
                                        justify="space-between",
                                        style={
                                            "align-content": "center",
                                            "align-items": "center",
                                            "width": "95%",
                                        },
                                        slots={
                                            "default": [
                                                VarNameInput(),
                                                VarTypeSelect(),
                                            ]
                                        },
                                    ),
                                    NButton(
                                        style={"width": "5%"},
                                        type="error",
                                        size="small",
                                        circle=True,
                                        level="tertiary",
                                        onClick=OperateFunctionProp(
                                            [
                                                REMOVERESULT4OUT_FuncProp(
                                                    Arg=FuncArg_REMOVERESULT4OUT(
                                                        ResultId=VBindProp(
                                                            [VFOR_DATA, "@RID"]
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
                        ),
                    ),
                ]
            },
        )


EXPORT_UI = UI_CodeOutput

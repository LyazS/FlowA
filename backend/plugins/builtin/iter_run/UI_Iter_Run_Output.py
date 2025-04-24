from typing import List, Dict, Union, Literal, Any
from pydantic import BaseModel
from app.uisdk import *
from app.schemas.VFNodeInterface import (
    VFNodeConnectionType,
    VFNodeContentDataConfig,
    VFNodeContentData,
)
from ..UI_Components.Header import Header
from ..UI_Components.RefVarSelect import UI_RefVarSelect
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


class UI_Iter_Run_Output(NFlex):
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
                                Header(type="info", text="输出数组"),
                                NButton(
                                    type="info",
                                    text=True,
                                    onClick=FunctionProp(
                                        Funcs=[
                                            ADDRESULT2OUT_FuncProp(
                                                Arg=FuncArg_ADDRESULT2OUT(
                                                    HandleId=ValueProp("output"),
                                                    Result=VFNodeContentData(
                                                        Label="",
                                                        Type="List",
                                                        Data=[],
                                                        Config=VFNodeContentDataConfig(
                                                            Ref=None
                                                        ),
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
                                                UI_RefVarSelect(
                                                    size="small",
                                                    style={"width": "50%"},
                                                    options=VBindProp(
                                                        [
                                                            CONNECT_DATA,
                                                            "--node",
                                                            CONNECT_CUR_NODE,
                                                            "--handle",
                                                            VFNodeConnectionType.Self,
                                                            "--hid",
                                                            "attach_output",
                                                            "--outfmt",
                                                            CONNECT_DATA_TO_SELECT,
                                                            "--level",
                                                            CONNECT_VAR_LEVEL,
                                                        ]
                                                    ),
                                                    value=VModelProp(
                                                        [
                                                            THIS_NODE_DATA,
                                                            "Results",
                                                            "ById",
                                                            VBindProp(
                                                                [VFOR_DATA, "@RID"]
                                                            ),
                                                            "Config",
                                                            "Ref",
                                                        ]
                                                    ),
                                                ),
                                            ]
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
                ],
            },
        )


EXPORT_UI = UI_Iter_Run_Output

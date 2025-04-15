from typing import Optional
from pydantic import BaseModel
from app.schemas.VFNodeInterface import VFNodeContentData
from app.uisdk import *
from .Header import Header
from .NFlex import NFlex
from .NButton import NButton


class UI_CodeEditor(NFlex):
    def __init__(self, useDisabled: Optional[bool] = None):
        otherProps = (
            {
                "disabled": useDisabled,
            }
            if useDisabled is not None
            else {}
        )
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
                                            OPENEDITOR_FuncProp(
                                                Arg=FuncArg_OPENEDITOR(
                                                    DstPath=[
                                                        THIS_NODE_DATA,
                                                        "Payloads",
                                                        "ById",
                                                        PAYLOADS_ID,
                                                        "Data",
                                                    ],
                                                    Language="python",
                                                )
                                            )
                                        ]
                                    ),
                                    otherProps=otherProps,
                                    slots={
                                        "default": SpanComponent(
                                            Type=ComponentType.VALUE, Data="编辑"
                                        ),
                                        "icon": NormalComponent(Type="CreateOutline"),
                                    },
                                ),
                            ]
                        },
                    ),
                    NormalComponent(
                        Type="NCode",
                        Props={
                            "word-wrap": True,
                            "language": VBindProp(
                                Data=[
                                    THIS_NODE_DATA,
                                    "Payloads",
                                    "ById",
                                    PAYLOADS_ID,
                                    "Config",
                                    "Language",
                                ]
                            ),
                            "code": VModelProp(
                                Data=[
                                    THIS_NODE_DATA,
                                    "Payloads",
                                    "ById",
                                    PAYLOADS_ID,
                                    "Data",
                                ]
                            ),
                        },
                    ),
                ]
            },
        )

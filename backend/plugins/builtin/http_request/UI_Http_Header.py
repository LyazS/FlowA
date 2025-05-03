from typing import List, Dict, Union, Literal, Optional
from pydantic import BaseModel
from app.schemas.VFNodeInterface import VFNodeContentData
from app.uisdk import *

from ..UI_Components.Header import Header
from ..UI_Components.NInput import NInput, NInputAutoSize
from ..UI_Components.NButton import NButton
from ..UI_Components.NFlex import NFlex
from .http_request import HttpRequestMethod, HttpRequestConfig_HEADER


class UI_http_header(NFlex):
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
                                                    ItemValue=HttpRequestConfig_HEADER(
                                                        Key="",
                                                        Value="",
                                                    ),
                                                )
                                            )
                                        ]
                                    ),
                                    slots={
                                        "default": SpanComponent(
                                            ValueProp("新增Header")
                                        ),
                                        "icon": NormalComponent(Type="Add"),
                                    },
                                ),
                            ]
                        },
                    ),
                    NFlex(
                        vertical=True,
                        slots={
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
                                ItemLabel="@HeaderItem",
                                IndexLabel="@HeaderIndex",
                                Template=NFlex(
                                    vertical=False,
                                    wrap=False,
                                    justify="space-between",
                                    style={
                                        "align-content": "center",
                                        "align-items": "center",
                                    },
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
                                                        NInput(
                                                            style={"width": "50%"},
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
                                                                    VBindProp(
                                                                        [
                                                                            VFOR_DATA,
                                                                            "@HeaderIndex",
                                                                        ]
                                                                    ),
                                                                    "Key",
                                                                ]
                                                            ),
                                                        ),
                                                        NInput(
                                                            style={"width": "50%"},
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
                                                                    VBindProp(
                                                                        [
                                                                            VFOR_DATA,
                                                                            "@HeaderIndex",
                                                                        ]
                                                                    ),
                                                                    "Value",
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
                                                                    [
                                                                        VFOR_DATA,
                                                                        "@HeaderIndex",
                                                                    ]
                                                                ),
                                                            ),
                                                        )
                                                    ]
                                                ),
                                                slots={
                                                    "icon": NormalComponent(
                                                        Type="Close"
                                                    ),
                                                },
                                            ),
                                        ]
                                    },
                                ),
                            )
                        },
                    ),
                ],
            },
        )


EXPORT_UI = UI_http_header

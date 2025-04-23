from typing import List, Dict, Union, Literal, Optional
from pydantic import BaseModel
from app.schemas.VFNodeInterface import VFNodeContentData
from app.uisdk import *

from ..UI_Components.Header import Header
from ..UI_Components.NInput import NInput, NInputAutoSize
from ..UI_Components.NButton import NButton
from ..UI_Components.NFlex import NFlex
from .http_request import (
    HttpRequestMethod,
    HttpRequestBodyType,
    HttpRequestBody_XWWWFORMURL,
    HttpRequestBody_FORMDATA,
    HttpRequestConfig_BODY,
)


class UI_http_body(NFlex):
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
                                                    CONTEXT_FUNCTION,
                                                    PAYLOADS_ID,
                                                ]
                                            ),
                                            "Label",
                                        ]
                                    ),
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
                                                CONTEXT_FUNCTION,
                                                PAYLOADS_ID,
                                            ]
                                        ),
                                        "Data",
                                        "Content2",
                                    ]
                                ),
                                ItemLabel="@XWWWFORMURLItem",
                                IndexLabel="@XWWWFORMURLIndex",
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
                                                                            CONTEXT_FUNCTION,
                                                                            PAYLOADS_ID,
                                                                        ]
                                                                    ),
                                                                    "Data",
                                                                    "Content2",
                                                                    VBindProp(
                                                                        [
                                                                            VFOR_DATA,
                                                                            "@XWWWFORMURLIndex",
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
                                                                            CONTEXT_FUNCTION,
                                                                            PAYLOADS_ID,
                                                                        ]
                                                                    ),
                                                                    "Data",
                                                                    "Content2",
                                                                    VBindProp(
                                                                        [
                                                                            VFOR_DATA,
                                                                            "@XWWWFORMURLIndex",
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
                                                                            [
                                                                                CONTEXT_FUNCTION,
                                                                                PAYLOADS_ID,
                                                                            ]
                                                                        ),
                                                                        "Data",
                                                                        "Content2",
                                                                    ]
                                                                ),
                                                                ItemKey=VBindProp(
                                                                    [
                                                                        VFOR_DATA,
                                                                        "@XWWWFORMURLIndex",
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


EXPORT_UI = UI_http_body

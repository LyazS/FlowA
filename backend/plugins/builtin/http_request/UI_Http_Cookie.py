from typing import List, Dict, Union, Literal, Optional
from pydantic import BaseModel
from app.schemas.VFNodeInterface import VFNodeContentData, VarType
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
    HttpRequestConfig_COOKIE,
)


class http_cookie_data(NFlex):
    def __init__(self):
        super().__init__(
            vertical=False,
            wrap=False,
            justify="space-between",
            style={"align-content": "center", "align-items": "center", "width": "95%"},
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
                                VBindProp([VFOR_DATA, "@CookieIndex"]),
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
                                VBindProp([VFOR_DATA, "@CookieIndex"]),
                                "Value",
                            ]
                        ),
                    ),
                ]
            },
        )


class UI_http_cookie(NFlex):
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
                                                    ItemValue=HttpRequestConfig_COOKIE(
                                                        Key="", Value=""
                                                    ),
                                                )
                                            )
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
                                ItemLabel="@CookieItem",
                                IndexLabel="@CookieIndex",
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
                                            http_cookie_data(),
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
                                                                        "@CookieIndex",
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


EXPORT_UI = UI_http_cookie

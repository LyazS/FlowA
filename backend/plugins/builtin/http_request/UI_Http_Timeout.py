from typing import List, Dict, Union, Literal, Optional
from pydantic import BaseModel
from app.schemas.VFNodeInterface import VFNodeContentData, VarType
from app.uisdk import *

from ..UI_Components.Header import Header
from ..UI_Components.NInput import NInput, NInputAutoSize
from ..UI_Components.NButton import NButton
from ..UI_Components.NText import NText
from ..UI_Components.NFlex import NFlex
from .http_request import (
    HttpRequestMethod,
    HttpRequestBodyType,
    HttpRequestBody_XWWWFORMURL,
    HttpRequestBody_FORMDATA,
    HttpRequestConfig_BODY,
    HttpRequestConfig_COOKIE,
    HttpRequestConfig_TIMEOUT,
)


class UI_Http_Timeout(NFlex):
    def __init__(self):
        super().__init__(
            vertical=True,
            slots={
                "default": [
                    Header(
                        type="error",
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
                    NFlex(
                        vertical=False,
                        wrap=False,
                        justify="flex-start",
                        style={"align-content": "center", "align-items": "center"},
                        slots={
                            "default": [
                                NText(
                                    slots={
                                        "default": SpanComponent(
                                            ValueProp("连接超时（秒）")
                                        )
                                    }
                                ),
                                NormalComponent(
                                    Type="NInputNumber",
                                    Props={
                                        "size": "small",
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
                                                "Connect",
                                            ]
                                        ),
                                        "precision": 2,
                                        "min": 0,
                                    },
                                ),
                            ]
                        },
                    ),
                    NFlex(
                        vertical=False,
                        wrap=False,
                        justify="flex-start",
                        style={"align-content": "center", "align-items": "center"},
                        slots={
                            "default": [
                                NText(
                                    slots={
                                        "default": SpanComponent(
                                            ValueProp("读取超时（秒）")
                                        )
                                    }
                                ),
                                NormalComponent(
                                    Type="NInputNumber",
                                    Props={
                                        "size": "small",
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
                                                "Read",
                                            ]
                                        ),
                                        "precision": 2,
                                        "min": 0,
                                    },
                                ),
                            ]
                        },
                    ),
                    NFlex(
                        vertical=False,
                        wrap=False,
                        justify="flex-start",
                        style={"align-content": "center", "align-items": "center"},
                        slots={
                            "default": [
                                NText(
                                    slots={
                                        "default": SpanComponent(
                                            ValueProp("写入超时（秒）")
                                        )
                                    }
                                ),
                                NormalComponent(
                                    Type="NInputNumber",
                                    Props={
                                        "size": "small",
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
                                                "Write",
                                            ]
                                        ),
                                        "precision": 2,
                                        "min": 0,
                                    },
                                ),
                            ]
                        },
                    ),
                ],
            },
        )


EXPORT_UI = UI_Http_Timeout

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
    HttpResponseFormat,
)


class UI_Http_ReturnFormat(NFlex):
    def __init__(self):
        super().__init__(
            vertical=True,
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
                    NormalComponent(
                        Type="NSelect",
                        Props={
                            "size": "medium",
                            # "style": {"width": "10em"},
                            "options": [
                                {
                                    "label": "JSON-强制转换为JSON格式",
                                    "value": HttpResponseFormat.JSON,
                                },
                                {
                                    "label": "TEXT-纯文本格式",
                                    "value": HttpResponseFormat.TEXT,
                                },
                                {
                                    "label": "BINARY-二进制文件格式",
                                    "value": HttpResponseFormat.BINARY,
                                },
                                {
                                    "label": "IMAGE-PIL图片格式",
                                    "value": HttpResponseFormat.IMAGE,
                                },
                            ],
                            "value": VModelProp(
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
                                ]
                            ),
                        },
                    ),
                ],
            },
        )


EXPORT_UI = UI_Http_ReturnFormat

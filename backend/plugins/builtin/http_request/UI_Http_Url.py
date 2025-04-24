from typing import List, Dict, Union, Literal, Optional
from pydantic import BaseModel
from app.schemas.VFNodeInterface import VFNodeContentData
from app.uisdk import *

from ..UI_Components.Header import Header
from ..UI_Components.NInput import NInput, NInputAutoSize
from ..UI_Components.NButton import NButton
from ..UI_Components.NFlex import NFlex
from .http_request import HttpRequestMethod


class UI_http_url(NFlex):
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
                    NFlex(
                        vertical=False,
                        wrap=False,
                        justify="space-between",
                        style={"align-content": "center", "align-items": "center"},
                        slots={
                            "default": [
                                NormalComponent(
                                    Type="NSelect",
                                    Props={
                                        "size": "medium",
                                        "style": {"width": "8em"},
                                        "options": [
                                            {
                                                "label": HttpRequestMethod.GET,
                                                "value": HttpRequestMethod.GET,
                                            },
                                            {
                                                "label": HttpRequestMethod.POST,
                                                "value": HttpRequestMethod.POST,
                                            },
                                            {
                                                "label": HttpRequestMethod.PUT,
                                                "value": HttpRequestMethod.PUT,
                                            },
                                            {
                                                "label": HttpRequestMethod.DELETE,
                                                "value": HttpRequestMethod.DELETE,
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
                                                "Method",
                                            ]
                                        ),
                                    },
                                ),
                                NInput(
                                    style={"flex": "1"},
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
                                            "Url",
                                        ]
                                    ),
                                )
                            ]
                        },
                    ),
                ],
            },
        )


EXPORT_UI = UI_http_url

from typing import List, Dict, Union, Literal, Any, Optional
from pydantic import BaseModel
from app.uisdk import *
from app.schemas.VFNodeInterface import VFNodeConnectionType
from ..UI_Components.Header import Header
from ..UI_Components.RefVarSelect import UI_RefVarSelect
from ..UI_Components.NFlex import NFlex
from .iter_retry import RetryType


class UI_ITER_RETRY_INOUT(NFlex):
    def __init__(self):
        super().__init__(
            vertical=True,
            slots={
                "default": [
                    Header(
                        type="warning",
                        text=ValueProp(Data="变量设置"),
                    ),
                    NFlex(
                        vertical=False,
                        wrap=False,
                        justify="flex-start",
                        style={"align-content": "center", "align-items": "center"},
                        slots={
                            "default": [
                                NormalComponent(
                                    Type="NTag",
                                    Props={
                                        "type": "info",
                                        "bordered": False,
                                        "size": "medium",
                                        "style": {"width": "5em"},
                                    },
                                    Slots={
                                        "default": SpanComponent(
                                            Type=ComponentType.VBIND,
                                            Data=[
                                                THIS_NODE_DATA,
                                                "Payloads",
                                                "ById",
                                                "D_IN_NODE",
                                                "Label",
                                            ],
                                        )
                                    },
                                ),
                                UI_RefVarSelect(
                                    value=VModelProp(
                                        Data=[
                                            THIS_NODE_DATA,
                                            "Payloads",
                                            "ById",
                                            "D_IN_NODE",
                                            "Data",
                                        ]
                                    ),
                                    options=VBindProp(
                                        Data=[
                                            CONNECT_DATA_TO_SELECT,
                                            VFNodeConnectionType.Self,
                                            "self",
                                        ]
                                    ),
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
                                NormalComponent(
                                    Type="NTag",
                                    Props={
                                        "type": "info",
                                        "bordered": False,
                                        "size": "medium",
                                        "style": {"width": "5em"},
                                    },
                                    Slots={
                                        "default": SpanComponent(
                                            Type=ComponentType.VBIND,
                                            Data=[
                                                THIS_NODE_DATA,
                                                "Payloads",
                                                "ById",
                                                "D_OUT_NODE",
                                                "Label",
                                            ],
                                        )
                                    },
                                ),
                                UI_RefVarSelect(
                                    value=VModelProp(
                                        Data=[
                                            THIS_NODE_DATA,
                                            "Payloads",
                                            "ById",
                                            "D_OUT_NODE",
                                            "Data",
                                        ]
                                    ),
                                    options=VBindProp(
                                        Data=[
                                            CONNECT_DATA_TO_SELECT,
                                            VFNodeConnectionType.Self,
                                            "attach_output",
                                        ]
                                    ),
                                ),
                            ]
                        },
                    ),
                ],
            },
        )


EXPORT_UI = UI_ITER_RETRY_INOUT

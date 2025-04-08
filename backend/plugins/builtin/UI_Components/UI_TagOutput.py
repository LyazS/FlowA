from pydantic import BaseModel
from app.uisdk import *
from app.schemas.VFNodeInterface import VFNodeConnectionType
from .Header import Header
from .NText import NText
from .NFlex import NFlex


class handleTag(NormalComponent):
    def __init__(self):
        super().__init__(
            Type="NDivider",
            Props={
                "title-placement": "left",
                "style": {
                    "width": "75%",
                    "margin": 0,
                },
            },
            Slots={
                "default": NormalComponent(
                    Type="NText",
                    Props={
                        "type": "warning",
                        "strong": True,
                    },
                    Slots={
                        "default": SpanComponent(
                            Type=ComponentType.VBIND,
                            Data=[
                                VFOR_DATA,
                                "@ConnectHandles",
                                "Label",
                            ],
                        )
                    },
                ),
            },
        )


class outputTag(NFlex):
    def __init__(self):
        super().__init__(
            vertical=True,
            slots={
                "default": [
                    ForLoopComponent(
                        Items=VBindProp(
                            Data=[
                                VFOR_DATA,
                                "@ConnectHandles",
                                "Data",
                            ]
                        ),
                        ItemLabel="@ConnectItems",
                        IndexLabel="@ItemIndex",
                        Template=NFlex(
                            vertical=False,
                            wrap=False,
                            justify="flex-start",
                            style={
                                "align-content": "center",
                                "align-items": "center",
                                "width": "50%",
                                "margin": 0,
                                "padding-left": "50px",
                            },
                            slots={
                                "default": [
                                    NText(
                                        depth=2,
                                        slots={
                                            "default": SpanComponent(
                                                Type=ComponentType.VBIND,
                                                Data=[
                                                    VFOR_DATA,
                                                    "@ConnectItems",
                                                    "DataLabel",
                                                ],
                                            ),
                                        },
                                    ),
                                    NText(
                                        depth=2,
                                        slots={
                                            "default": SpanComponent(
                                                Type=ComponentType.VALUE,
                                                Data=" - ",
                                            ),
                                        },
                                    ),
                                    NText(
                                        depth=2,
                                        type="info",
                                        italic=True,
                                        slots={
                                            "default": SpanComponent(
                                                Type=ComponentType.VBIND,
                                                Data=[
                                                    VFOR_DATA,
                                                    "@ConnectItems",
                                                    "DataType",
                                                ],
                                            ),
                                        },
                                    ),
                                ],
                            },
                        ),
                    ),
                ]
            },
        )


class outputCard(NormalComponent):
    def __init__(self):
        super().__init__(
            Type="NCard",
            Props={
                "bordered": True,
                "hoverable": True,
                "size": "small",
                "style": {
                    "width": "100%",
                    "margin-bottom": "10px",
                },
            },
            Slots={
                "header": handleTag(),
                "default": outputTag(),
            },
        )


class UI_TAG_OUTPUTS(NFlex):
    def __init__(self):
        super().__init__(
            vertical=True,
            slots={
                "default": [
                    Header(type="info", text="输出变量"),
                    ForLoopComponent(
                        Items=VBindProp(
                            Data=[
                                CONNECT_DATA_HANDLE,
                                VFNodeConnectionType.Outputs,
                            ]
                        ),
                        ItemLabel="@ConnectHandles",
                        IndexLabel="@HandleId",
                        Template=NFlex(
                            vertical=True,
                            slots={
                                "default": outputCard(),
                            },
                        ),
                    ),
                ]
            },
        )


EXPORT_UI = UI_TAG_OUTPUTS

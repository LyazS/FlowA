from pydantic import BaseModel
from app.uisdk import *
from .Header import Header
from .RefVarSelect import UI_RefVarSelect
from app.schemas.VFNodeInterface import VFNodeConnectionType


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
                                "default": [
                                    NormalComponent(
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
                                    ),
                                    NFlex(
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
                                                    Template=NormalComponent(
                                                        Type="NDivider",
                                                        Props={
                                                            "title-placement": "left",
                                                            "style": {
                                                                "width": "50%",
                                                                "margin": 0,
                                                                "padding-left": "20px",
                                                            },
                                                        },
                                                        Slots={
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
                                    ),
                                ]
                            },
                        ),
                    ),
                ]
            },
        )


EXPORT_UI = UI_TAG_OUTPUTS

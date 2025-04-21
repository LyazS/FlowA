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
                            VBindProp(
                                [
                                    THIS_NODE_DATA,
                                    "Connections",
                                    VFNodeConnectionType.Outputs,
                                    "ById",
                                    VBindProp([VFOR_DATA, "@ConnectHandles"]),
                                    "Label",
                                ]
                            ),
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
                            [
                                CONNECT_DATA,
                                "--node",
                                CONNECT_CUR_NODE,
                                "--handle",
                                VFNodeConnectionType.Outputs,
                                "--hid",
                                VBindProp([VFOR_DATA, "@ConnectHandles"]),
                                "--outfmt",
                                CONNECT_ALL_DATA,
                                "--level",
                                CONNECT_VAR_LEVEL,
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
                                                VBindProp(
                                                    [
                                                        THIS_NODE_DATA,
                                                        "Results",
                                                        "ById",
                                                        VBindProp(
                                                            [
                                                                VFOR_DATA,
                                                                "@ConnectItems",
                                                                "Path",
                                                                "ContentId",
                                                            ]
                                                        ),
                                                        "Label",
                                                    ]
                                                ),
                                            ),
                                        },
                                    ),
                                    NText(
                                        depth=2,
                                        slots={
                                            "default": SpanComponent(ValueProp(" - ")),
                                        },
                                    ),
                                    NText(
                                        depth=2,
                                        type="info",
                                        italic=True,
                                        slots={
                                            "default": SpanComponent(
                                                VBindProp(
                                                    [
                                                        THIS_NODE_DATA,
                                                        "Results",
                                                        "ById",
                                                        VBindProp(
                                                            [
                                                                VFOR_DATA,
                                                                "@ConnectItems",
                                                                "Path",
                                                                "ContentId",
                                                            ]
                                                        ),
                                                        "Type",
                                                    ]
                                                ),
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
                                CONNECT_DATA,
                                "--node",
                                CONNECT_CUR_NODE,
                                "--handle",
                                VFNodeConnectionType.Outputs,
                                "--outfmt",
                                CONNECT_ALL_DATA,
                                "--level",
                                CONNECT_HANDLE_LEVEL,
                                "--notop",
                            ]
                        ),
                        ItemLabel="@ConnectHandles",
                        IndexLabel="@ConnectHandlesIndex",
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

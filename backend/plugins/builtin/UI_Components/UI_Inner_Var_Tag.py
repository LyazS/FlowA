from typing import List, Dict, Union, Literal, Any
from pydantic import BaseModel
from app.uisdk import *
from app.schemas.VFNodeInterface import VFNodeConnectionType
from .Header import Header
from .RefVarSelect import UI_RefVarSelect
from .NText import NText
from .NFlex import NFlex


class TagPath(BaseModel):
    label_path: List[str | int]
    type_path: List[str | int]


class innerTag(NFlex):
    def __init__(self, label_path: List[str | int], type_path: List[str | int]):
        super().__init__(
            vertical=False,
            wrap=False,
            justify="flex-start",
            style={
                "align-content": "center",
                "align-items": "center",
                "width": "50%",
                "margin": 0,
                "padding-left": "20px",
            },
            slots={
                "default": [
                    NText(
                        depth=2,
                        slots={
                            "default": SpanComponent(
                                Type=ComponentType.VBIND,
                                Data=label_path,
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
                                Data=type_path,
                            ),
                        },
                    ),
                ],
            },
        )


class innerCard(NormalComponent):
    def __init__(self, tagpaths: List[TagPath]):
        super().__init__(
            Type="NCard",
            Props={
                "bordered": True,
                "hoverable": True,
                "size": "small",
                "style": {
                    "width": "100%",
                },
            },
            Slots={
                "default": NFlex(
                    vertical=True,
                    slots={
                        "default": [
                            innerTag(
                                label_path=tagpath.label_path,
                                type_path=tagpath.type_path,
                            )
                            for tagpath in tagpaths
                        ]
                    },
                )
            },
        )


class UI_Inner_Var_Tag(NFlex):
    def __init__(self, tagpaths: List[TagPath]):
        super().__init__(
            vertical=True,
            slots={
                "default": [
                    Header(type="success", text="内置变量"),
                    innerCard(tagpaths),
                ],
            },
        )

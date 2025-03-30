from typing import List, Dict, Union, Literal
from pydantic import BaseModel
from app.schemas.VFNodeInterface import VFNodeContentData
from app.uisdk import *
from ..UI_Components.Header import Header
from ..UI_Components.RefVarSelect import UI_RefVarSelect

typeoptions = [
    {"label": "引用", "value": "Ref"},
    {"label": "常量", "value": "Const"},
]
typeoptionsWnull = [
    {"label": "引用", "value": "Ref"},
    {"label": "常量", "value": "Const"},
    {"label": "缺省", "value": "Null"},
]


class SingleAttrSelect(NFlex):
    def __init__(self, attr_path: List[Union[str, int]], options: List[Dict[str, str]]):
        super().__init__(
            vertical=False,
            wrap=False,
            justify="space-between",
            style={"align-content": "center", "align-items": "center"},
            slots={
                "default": [
                    NormalComponent(
                        Type="NTag",
                        Props={
                            "type": "info",
                            "bordered": False,
                        },
                        Slots={
                            "default": SpanComponent(
                                Type=ComponentType.VBIND, Data=attr_path + ["Label"]
                            )
                        },
                    ),
                    NormalComponent(
                        Type="NSelect",
                        Props={
                            "size": "tiny",
                            "consistent-menu-width": False,
                            "style": {"width": "8em"},
                            "options": typeoptions,
                            "value": VModelProp(Data=attr_path + ["Data", "Type"]),
                        },
                    ),
                    UI_RefVarSelect(
                        value=VModelProp(Data=attr_path + ["Data", "Content"]),
                        size="tiny",
                        IfCondition=CompareCondition(
                            Left=VBindProp(Data=attr_path + ["Data", "Type"]),
                            Operator="==",
                            Right=PropVar(Data="Ref"),
                        ),
                    ),
                    NormalComponent(
                        Type="NSelect",
                        Props={
                            "size": "tiny",
                            "consistent-menu-width": False,
                            "options": typeoptions,
                            "value": VModelProp(Data=attr_path + ["Data", "Content"]),
                        },
                    ),
                ]
            },
        )

    pass


class UI_LLM_ATTRIBUTE_TAG(NFlex):
    def __init__(self):
        super().__init__(
            vertical=True,
            slots={
                "default": [
                    Header(type="success", text="模型设置"),
                ]
            },
        )


EXPORT_UI = UI_LLM_ATTRIBUTE_TAG

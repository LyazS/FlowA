from typing import List, Dict, Union, Literal, Any
from pydantic import BaseModel
from app.uisdk import *
from ..UI_Components.Header import Header
from ..UI_Components.RefVarSelect import UI_RefVarSelect
from app.schemas.VFNodeInterface import VFNodeConnectionType


class UI_Iter_Run_Iter_Array(NFlex):
    def __init__(self):
        super().__init__(
            vertical=True,
            slots={
                "default": [
                    Header(
                        type="warning",
                        text=VBindProp(
                            Data=[
                                THIS_NODE_DATA,
                                "Payloads",
                                "ById",
                                PAYLOADS_ID,
                                "Label",
                            ]
                        ),
                    ),
                    UI_RefVarSelect(
                        size="medium",
                        options=VBindProp(
                            Data=[
                                CONNECT_DATA_TO_SELECT,
                                VFNodeConnectionType.Self,
                                "self",
                            ]
                        ),
                        value=VModelProp(
                            Data=[
                                THIS_NODE_DATA,
                                "Payloads",
                                "ById",
                                PAYLOADS_ID,
                                "Data",
                            ],
                        ),
                    ),
                ],
            },
        )


EXPORT_UI = UI_Iter_Run_Iter_Array

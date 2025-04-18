from typing import List, Dict, Union, Literal, Any
from pydantic import BaseModel
from app.uisdk import *
from app.schemas.VFNodeInterface import VFNodeConnectionType
from ..UI_Components.Header import Header
from ..UI_Components.RefVarSelect import UI_RefVarSelect
from ..UI_Components.NFlex import NFlex


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
                                CONNECT_DATA,
                                "--node",
                                CONNECT_CUR_NODE,
                                "--handle",
                                VFNodeConnectionType.Self,
                                "--hid",
                                "self",
                                "--outfmt",
                                CONNECT_DATA_TO_SELECT,
                                "--level",
                                CONNECT_VAR_LEVEL,
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

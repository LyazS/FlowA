from typing import Optional, Dict, List, Union, Literal
from app.uisdk import *
from app.schemas.VFNodeInterface import VarType
from plugins.builtin.UI_Components.NFlex import NFlex
from plugins.builtin.UI_Components.NInput import NInput
from plugins.builtin.UI_Components.NButton import NButton
from plugins.builtin.UI_Components.Header import Header
from plugins.builtin.UI_Components.RefVarSelect import UI_RefVarSelect
from plugins.builtin.UI_Components.UI_FileUpload import UI_FileUpload


class UI_CF_Workflow(NFlex):
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
                                        COMPONENT_CONTEXT,
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
                                        "value": VModelProp(
                                            [
                                                THIS_NODE_DATA,
                                                "Payloads",
                                                "ById",
                                                VBindProp(
                                                    [
                                                        COMPONENT_CONTEXT,
                                                        PAYLOADS_ID,
                                                    ]
                                                ),
                                                "Data",
                                                "Type",
                                            ]
                                        ),
                                        "options": [
                                            {"label": "工作流", "value": VarType.File},
                                            {"label": "引用", "value": VarType.Ref},
                                        ],
                                    },
                                ),
                                UI_FileUpload(
                                    value=[
                                        THIS_NODE_DATA,
                                        "Payloads",
                                        "ById",
                                        VBindProp(
                                            [
                                                COMPONENT_CONTEXT,
                                                PAYLOADS_ID,
                                            ]
                                        ),
                                        "Data",
                                        "ValueJson",
                                    ],
                                    width="70%",
                                    fileType=UploadFileInfoType.STRING,
                                    filterType=[".json"],
                                    IfCondition=CompareCondition(
                                        Left=VBindProp(
                                            [
                                                THIS_NODE_DATA,
                                                "Payloads",
                                                "ById",
                                                VBindProp(
                                                    [
                                                        COMPONENT_CONTEXT,
                                                        PAYLOADS_ID,
                                                    ]
                                                ),
                                                "Data",
                                                "Type",
                                            ]
                                        ),
                                        Operator="==",
                                        Right=ValueProp(VarType.File),
                                    ),
                                ),
                                UI_RefVarSelect(
                                    style={"width": "70%"},
                                    value=VModelProp(
                                        [
                                            THIS_NODE_DATA,
                                            "Payloads",
                                            "ById",
                                            VBindProp(
                                                [
                                                    COMPONENT_CONTEXT,
                                                    PAYLOADS_ID,
                                                ]
                                            ),
                                            "Data",
                                            "ValueRef",
                                        ]
                                    ),
                                    options=VBindProp(
                                        [
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
                                            "--filtertypes",
                                            VarType.String,
                                        ]
                                    ),
                                    IfCondition=CompareCondition(
                                        Left=VBindProp(
                                            [
                                                THIS_NODE_DATA,
                                                "Payloads",
                                                "ById",
                                                VBindProp(
                                                    [
                                                        COMPONENT_CONTEXT,
                                                        PAYLOADS_ID,
                                                    ]
                                                ),
                                                "Data",
                                                "Type",
                                            ]
                                        ),
                                        Operator="==",
                                        Right=ValueProp(VarType.Ref),
                                    ),
                                ),
                            ]
                        },
                    ),
                ]
            },
        )


EXPORT_UI = UI_CF_Workflow

from app.uisdk import *
from app.schemas.VFNodeInterface import VarType
from plugins.builtin.UI_Components.NFlex import NFlex
from plugins.builtin.UI_Components.NInput import NInput
from plugins.builtin.UI_Components.RefVarSelect import UI_RefVarSelect
from plugins.builtin.UI_Components.Header import Header


class UI_Image_Read_Path(NFlex):
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
                    # 类型选择
                    NFlex(
                        vertical=False,
                        wrap=False,
                        justify="space-between",
                        style={"align-content": "center", "align-items": "center"},
                        slots={
                            "default": [
                                # 类型选择下拉框
                                NormalComponent(
                                    Type="NSelect",
                                    Props={
                                        "style": {"width": "30%"},
                                        "size": "small",
                                        "options": [
                                            {
                                                "label": "字符串",
                                                "value": VarType.String,
                                            },
                                            {"label": "引用", "value": VarType.Ref},
                                        ],
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
                                    },
                                ),
                                # 字符串输入
                                NInput(
                                    style={"width": "70%"},
                                    size="small",
                                    otherProps={"placeholder": "输入图片绝对路径"},
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
                                            "ValueStr",
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
                                        Right=ValueProp(VarType.String),
                                    ),
                                ),
                                # 引用选择
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
                                        ],
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


# 必须存在
EXPORT_UI = UI_Image_Read_Path

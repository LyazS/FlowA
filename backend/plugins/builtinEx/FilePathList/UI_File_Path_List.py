from app.uisdk import *
from app.schemas.VFNodeInterface import VarType
from plugins.builtin.UI_Components.NFlex import NFlex
from plugins.builtin.UI_Components.NInput import NInput
from plugins.builtin.UI_Components.NButton import NButton
from plugins.builtin.UI_Components.Header import Header
from .FilePathList import (
    FilePathListType,
    FilePathQuickSelect,
    FileImagePatterns,
    FileVideoPatterns,
)


class UI_File_Path_List(NFlex):
    def __init__(self):
        super().__init__(
            vertical=True,
            slots={
                "default": [
                    Header(
                        type="success",
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
                    NormalComponent(
                        Type="NRadioGroup",
                        Props={
                            "size": "small",
                            "name": "FilePathListType",
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
                        Slots={
                            "default": [
                                NormalComponent(
                                    Type="NRadio",
                                    Props={
                                        "key": "目录模式",
                                        "value": FilePathListType.DIR,
                                        "style": {"margin-right": "10px"},
                                    },
                                    Slots={
                                        "default": SpanComponent(ValueProp("目录模式")),
                                    },
                                ),
                                NormalComponent(
                                    Type="NRadio",
                                    Props={
                                        "key": "正则表达式",
                                        "value": FilePathListType.REGEX,
                                        "style": {"margin-right": "10px"},
                                    },
                                    Slots={
                                        "default": SpanComponent(
                                            ValueProp("正则表达式")
                                        ),
                                    },
                                ),
                            ]
                        },
                    ),
                    # 目录模式配置
                    NFlex(
                        vertical=True,
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
                            Right=ValueProp(FilePathListType.DIR),
                        ),
                        slots={
                            "default": [
                                # 目录输入
                                NFlex(
                                    vertical=False,
                                    wrap=False,
                                    justify="space-between",
                                    style={
                                        "align-content": "center",
                                        "align-items": "center",
                                        "margin-top": "10px",
                                    },
                                    slots={
                                        "default": [
                                            NormalComponent(
                                                Type="NTag",
                                                Props={
                                                    "bordered": False,
                                                    "type": "success",
                                                    "size": "medium",
                                                },
                                                Slots={
                                                    "default": SpanComponent(
                                                        ValueProp("目录")
                                                    )
                                                },
                                            ),
                                            NInput(
                                                style={"width": "80%"},
                                                size="small",
                                                placeholder="输入目录路径",
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
                                                        "Dir",
                                                    ]
                                                ),
                                            ),
                                        ]
                                    },
                                ),
                                # 文件名输入
                                NFlex(
                                    vertical=False,
                                    wrap=False,
                                    justify="space-between",
                                    style={
                                        "align-content": "center",
                                        "align-items": "center",
                                        "margin-top": "10px",
                                    },
                                    slots={
                                        "default": [
                                            NormalComponent(
                                                Type="NTag",
                                                Props={
                                                    "bordered": False,
                                                    "type": "success",
                                                    "size": "medium",
                                                },
                                                Slots={
                                                    "default": SpanComponent(
                                                        ValueProp("文件名")
                                                    )
                                                },
                                            ),
                                            NInput(
                                                style={"width": "80%"},
                                                size="small",
                                                placeholder="支持通配符，如 *.jpg",
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
                                                        "FileName",
                                                    ]
                                                ),
                                            ),
                                        ]
                                    },
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
                                                "QuickSelect",
                                            ]
                                        ),
                                        Operator="==",
                                        Right=ValueProp([]),
                                    ),
                                ),
                                # 快速选择
                                NFlex(
                                    vertical=False,
                                    wrap=False,
                                    justify="space-between",
                                    style={
                                        "align-content": "center",
                                        "align-items": "center",
                                        "margin-top": "10px",
                                    },
                                    slots={
                                        "default": [
                                            NormalComponent(
                                                Type="NTag",
                                                Props={
                                                    "bordered": False,
                                                    "type": "success",
                                                    "size": "medium",
                                                },
                                                Slots={
                                                    "default": SpanComponent(
                                                        ValueProp("快速选择后缀")
                                                    )
                                                },
                                            ),
                                            NormalComponent(
                                                Type="NCheckboxGroup",
                                                Props={
                                                    "style": {"width": "80%"},
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
                                                            "QuickSelect",
                                                        ]
                                                    ),
                                                },
                                                Slots={
                                                    "default": NFlex(
                                                        vertical=False,
                                                        wrap=False,
                                                        justify="flex-start",
                                                        slots={
                                                            "default": [
                                                                NormalComponent(
                                                                    Type="NPopover",
                                                                    Props={
                                                                        "trigger": "hover",
                                                                    },
                                                                    Slots={
                                                                        "trigger": NormalComponent(
                                                                            Type="NCheckbox",
                                                                            Props={
                                                                                "label": "图像",
                                                                                "value": FilePathQuickSelect.IMAGE,
                                                                            },
                                                                        ),
                                                                        "default": SpanComponent(
                                                                            ValueProp(
                                                                                "图像后缀: "
                                                                                + ", ".join(
                                                                                    FileImagePatterns
                                                                                )
                                                                            )
                                                                        ),
                                                                    },
                                                                ),
                                                                NormalComponent(
                                                                    Type="NPopover",
                                                                    Props={
                                                                        "trigger": "hover",
                                                                    },
                                                                    Slots={
                                                                        "trigger": NormalComponent(
                                                                            Type="NCheckbox",
                                                                            Props={
                                                                                "label": "视频",
                                                                                "value": FilePathQuickSelect.VIDEO,
                                                                            },
                                                                        ),
                                                                        "default": SpanComponent(
                                                                            ValueProp(
                                                                                "视频后缀: "
                                                                                + ", ".join(
                                                                                    FileVideoPatterns
                                                                                )
                                                                            )
                                                                        ),
                                                                    },
                                                                ),
                                                            ]
                                                        },
                                                    )
                                                },
                                            ),
                                        ]
                                    },
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
                                                "FileName",
                                            ]
                                        ),
                                        Operator="==",
                                        Right=ValueProp(""),
                                    ),
                                ),
                            ]
                        },
                    ),
                    # 正则表达式模式配置
                    NFlex(
                        vertical=False,
                        wrap=False,
                        justify="space-between",
                        style={
                            "align-content": "center",
                            "align-items": "center",
                            "margin-top": "10px",
                        },
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
                            Right=ValueProp(FilePathListType.REGEX),
                        ),
                        slots={
                            "default": [
                                NormalComponent(
                                    Type="NTag",
                                    Props={
                                        "bordered": False,
                                        "type": "success",
                                        "size": "medium",
                                    },
                                    Slots={
                                        "default": SpanComponent(
                                            ValueProp("正则表达式")
                                        )
                                    },
                                ),
                                NInput(
                                    style={"width": "80%"},
                                    size="small",
                                    placeholder="输入正则表达式",
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
                                            "Regex",
                                        ]
                                    ),
                                ),
                            ]
                        },
                    ),
                    # 递归子目录开关
                    NFlex(
                        vertical=False,
                        wrap=False,
                        justify="flex-start",
                        style={
                            "align-content": "center",
                            "align-items": "center",
                            "margin-top": "10px",
                        },
                        slots={
                            "default": [
                                NormalComponent(
                                    Type="NTag",
                                    Props={
                                        "bordered": False,
                                        "type": "success",
                                        "size": "medium",
                                    },
                                    Slots={
                                        "default": SpanComponent(
                                            ValueProp("递归搜索子目录")
                                        )
                                    },
                                ),
                                NormalComponent(
                                    Type="NSwitch",
                                    Props={
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
                                                "Recursive",
                                            ]
                                        ),
                                    },
                                ),
                            ]
                        },
                    ),
                ]
            },
        )


# 必须存在
EXPORT_UI = UI_File_Path_List

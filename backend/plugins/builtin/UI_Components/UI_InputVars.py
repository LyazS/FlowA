from pydantic import BaseModel
from app.uisdk import *
from .Header import Header
from .RefVarSelect import UI_RefVarSelect


class DefaultInputVar(BaseModel):
    key: str = ""
    type: str = "String"
    valueStr: str = ""
    valueNum: int | float = 0
    valueBool: bool = False
    pass


class VarNameInput(NInput):
    def __init__(self):
        super().__init__(
            style={"width": "30%"},
            size="small",
            value=VModelProp(
                Data=[
                    THIS_NODE_DATA,
                    "Payloads",
                    "ById",
                    PAYLOADS_ID,
                    "Data",
                    "@Index",
                    "key",
                ]
            ),
        )


class VarTypeSelect(NormalComponent):
    def __init__(self):
        super().__init__(
            Type="NSelect",
            Props={
                "style": {"width": "20%"},
                "size": "small",
                "consistent-menu-width": False,
                "options": [
                    {"label": "引用", "value": "Ref"},
                    {"label": "字符串", "value": "String"},
                    {"label": "整数", "value": "Integer"},
                    {"label": "数字", "value": "Number"},
                    {"label": "布尔", "value": "Boolean"},
                ],
                "value": VModelProp(
                    Data=[
                        THIS_NODE_DATA,
                        "Payloads",
                        "ById",
                        PAYLOADS_ID,
                        "Data",
                        "@Index",
                        "type",
                    ]
                ),
            },
        )


class VarStringInput(NInput):
    def __init__(self):
        super().__init__(
            size="small",
            style={"width": "50%"},
            value=VModelProp(
                Data=[
                    THIS_NODE_DATA,
                    "Payloads",
                    "ById",
                    PAYLOADS_ID,
                    "Data",
                    "@Index",
                    "valueStr",
                ],
            ),
            IfCondition=CompareCondition(
                Left=VBindProp(
                    Data=[
                        THIS_NODE_DATA,
                        "Payloads",
                        "ById",
                        PAYLOADS_ID,
                        "Data",
                        "@Index",
                        "type",
                    ]
                ),
                Operator="==",
                Right=ValueProp(Data="String"),
            ),
        )


class VarIntegerInput(NormalComponent):
    def __init__(self):
        super().__init__(
            Type="NInputNumber",
            Props={
                "size": "small",
                "style": {"width": "50%"},
                "value": VModelProp(
                    Data=[
                        THIS_NODE_DATA,
                        "Payloads",
                        "ById",
                        PAYLOADS_ID,
                        "Data",
                        "@Index",
                        "valueNum",
                    ],
                ),
                "precision": 0,
            },
            IfCondition=CompareCondition(
                Left=VBindProp(
                    Data=[
                        THIS_NODE_DATA,
                        "Payloads",
                        "ById",
                        PAYLOADS_ID,
                        "Data",
                        "@Index",
                        "type",
                    ]
                ),
                Operator="==",
                Right=ValueProp(Data="Integer"),
            ),
        )


class VarNumberInput(NormalComponent):
    def __init__(self):
        super().__init__(
            Type="NInputNumber",
            Props={
                "size": "small",
                "style": {"width": "50%"},
                "value": VModelProp(
                    Data=[
                        THIS_NODE_DATA,
                        "Payloads",
                        "ById",
                        PAYLOADS_ID,
                        "Data",
                        "@Index",
                        "valueNum",
                    ],
                ),
            },
            IfCondition=CompareCondition(
                Left=VBindProp(
                    Data=[
                        THIS_NODE_DATA,
                        "Payloads",
                        "ById",
                        PAYLOADS_ID,
                        "Data",
                        "@Index",
                        "type",
                    ]
                ),
                Operator="==",
                Right=ValueProp(Data="Number"),
            ),
        )


class VarBooleanInput(NFlex):
    def __init__(self):
        super().__init__(
            justify="start",
            style={"width": "50%"},
            slots={
                "default": NormalComponent(
                    Type="NSwitch",
                    Props={
                        "size": "medium",
                        "style": {"width": "50%"},
                        "value": VModelProp(
                            Data=[
                                THIS_NODE_DATA,
                                "Payloads",
                                "ById",
                                PAYLOADS_ID,
                                "Data",
                                "@Index",
                                "valueBool",
                            ],
                        ),
                    },
                )
            },
            IfCondition=CompareCondition(
                Left=VBindProp(
                    Data=[
                        THIS_NODE_DATA,
                        "Payloads",
                        "ById",
                        PAYLOADS_ID,
                        "Data",
                        "@Index",
                        "type",
                    ]
                ),
                Operator="==",
                Right=ValueProp(Data="Boolean"),
            ),
        )

    pass


class UI_SingleInputVars(NFlex):
    def __init__(self):
        super().__init__(
            vertical=False,
            wrap=False,
            style={"align-content": "center", "align-items": "center", "width": "95%"},
            slots={
                "default": [
                    VarNameInput(),
                    VarTypeSelect(),
                    VarStringInput(),
                    VarIntegerInput(),
                    VarNumberInput(),
                    VarBooleanInput(),
                    UI_RefVarSelect(
                        size="small",
                        style={"width": "50%"},
                        options=VBindProp(
                            Data=[
                                CONNECT_OPTIONS,
                                "Self",
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
                                "@Index",
                                "valueStr",
                            ],
                        ),
                        IfCondition=CompareCondition(
                            Left=VBindProp(
                                Data=[
                                    THIS_NODE_DATA,
                                    "Payloads",
                                    "ById",
                                    PAYLOADS_ID,
                                    "Data",
                                    "@Index",
                                    "type",
                                ]
                            ),
                            Operator="==",
                            Right=ValueProp(Data="Ref"),
                        ),
                    ),
                ]
            },
        )


class UI_InputVars(NFlex):
    def __init__(self):
        super().__init__(
            vertical=True,
            slots={
                "default": [
                    NFlex(
                        vertical=False,
                        wrap=False,
                        justify="space-between",
                        style={"align-content": "center", "align-items": "center"},
                        slots={
                            "default": [
                                Header(type="success", text="输入变量"),
                                NButton(
                                    type="success",
                                    text=True,
                                    onClick=APPENDITEM_FuncProp(
                                        Arg=FuncArg_APPENDITEM(
                                            DstPath=[
                                                THIS_NODE_DATA,
                                                "Payloads",
                                                "ById",
                                                PAYLOADS_ID,
                                                "Data",
                                            ],
                                            ItemValue=DefaultInputVar(),
                                        )
                                    ),
                                    slots={
                                        "default": SpanComponent(
                                            Type=ComponentType.VALUE, Data="添加"
                                        ),
                                        "icon": NormalComponent(Type="Add"),
                                    },
                                ),
                            ]
                        },
                    ),
                    ForLoopComponent(
                        Items=VBindProp(
                            Data=[
                                THIS_NODE_DATA,
                                "Payloads",
                                "ById",
                                PAYLOADS_ID,
                                "Data",
                            ]
                        ),
                        ItemLabel="@Item",
                        IndexLabel="@Index",
                        Template=NFlex(
                            vertical=False,
                            wrap=False,
                            justify="space-between",
                            style={"align-content": "center", "align-items": "center"},
                            slots={
                                "default": [
                                    UI_SingleInputVars(),
                                    NButton(
                                        style={"width": "5%"},
                                        type="error",
                                        size="small",
                                        circle=True,
                                        level="tertiary",
                                        onClick=REMOVEITEM_FuncProp(
                                            Arg=FuncArg_REMOVEITEM(
                                                DstPath=[
                                                    THIS_NODE_DATA,
                                                    "Payloads",
                                                    "ById",
                                                    PAYLOADS_ID,
                                                    "Data",
                                                ],
                                                ItemKey=VBindProp(
                                                    Data=[
                                                        VFOR_DATA,
                                                        "@Index",
                                                    ]
                                                ),
                                            ),
                                        ),
                                        slots={
                                            "icon": NormalComponent(Type="Close"),
                                        },
                                    ),
                                ]
                            },
                        ),
                    ),
                ]
            },
        )


EXPORT_UI = UI_InputVars

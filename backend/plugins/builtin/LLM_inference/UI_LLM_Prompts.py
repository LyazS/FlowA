from typing import List, Dict, Union, Literal, Optional
from pydantic import BaseModel
from app.schemas.VFNodeInterface import VFNodeContentData
from app.uisdk import *
from .LLM_inference import (
    LLMSettingType,
    LLMSetting,
    LLMTypeOptions,
    LLMTypeOptionsWnull,
    LLMRoleOptions,
    LLMRole,
    SinglePrompt,
)
from ..UI_Components.Header import Header
from ..UI_Components.NInput import NInput, NInputAutoSize
from ..UI_Components.NButton import NButton
from ..UI_Components.NFlex import NFlex

DefaultPrompt = SinglePrompt(role=LLMRole.user, content="")


class UI_PromptOperate(NFlex):
    def __init__(self):
        super().__init__(
            vertical=False,
            wrap=False,
            justify="space-between",
            style={
                "align-content": "center",
                "align-items": "center",
                "margin-bottom": "1px",
            },
            slots={
                "default": [
                    NormalComponent(
                        Type="NSelect",
                        Props={
                            "size": "small",
                            "style": {"width": "100px", "margin-bottom": 0},
                            "options": LLMRoleOptions,
                            "value": VModelProp(
                                [
                                    THIS_NODE_DATA,
                                    "Payloads",
                                    "ById",
                                    VBindProp(
                                        [
                                            CONTEXT_FUNCTION,
                                            PAYLOADS_ID,
                                        ]
                                    ),
                                    "Data",
                                    VBindProp([VFOR_DATA, "@PromptIndex"]),
                                    "role",
                                ]
                            ),
                        },
                    ),
                    NButton(
                        style={"margin-bottom": 0},
                        type="warning",
                        text=True,
                        onClick=FunctionProp(
                            Funcs=[
                                OPENEDITOR_FuncProp(
                                    Arg=FuncArg_OPENEDITOR(
                                        DstPath=VBindProp(
                                            [
                                                THIS_NODE_DATA,
                                                "Payloads",
                                                "ById",
                                                VBindProp(
                                                    [
                                                        CONTEXT_FUNCTION,
                                                        PAYLOADS_ID,
                                                    ]
                                                ),
                                                "Data",
                                                VBindProp([VFOR_DATA, "@PromptIndex"]),
                                                "content",
                                            ]
                                        ),
                                        Language="text",
                                    )
                                )
                            ]
                        ),
                        slots={
                            "default": SpanComponent(ValueProp("编辑")),
                            "icon": NormalComponent(Type="CreateOutline"),
                        },
                    ),
                ]
            },
        )


class UI_PromptContent(NFlex):
    def __init__(self):
        super().__init__(
            vertical=False,
            wrap=False,
            justify="space-between",
            style={"align-content": "center", "align-items": "center"},
            slots={
                "default": [
                    NInput(
                        autosize=NInputAutoSize(minRows=3, maxRows=10),
                        type="textarea",
                        showCount=True,
                        value=VModelProp(
                            [
                                THIS_NODE_DATA,
                                "Payloads",
                                "ById",
                                VBindProp(
                                    [
                                        CONTEXT_FUNCTION,
                                        PAYLOADS_ID,
                                    ]
                                ),
                                "Data",
                                VBindProp([VFOR_DATA, "@PromptIndex"]),
                                "content",
                            ]
                        ),
                    ),
                    NButton(
                        style={"width": "5%"},
                        type="error",
                        size="small",
                        circle=True,
                        level="tertiary",
                        onClick=FunctionProp(
                            Funcs=[
                                REMOVEITEM_FuncProp(
                                    Arg=FuncArg_REMOVEITEM(
                                        DstPath=VBindProp(
                                            [
                                                THIS_NODE_DATA,
                                                "Payloads",
                                                "ById",
                                                VBindProp(
                                                    [
                                                        CONTEXT_FUNCTION,
                                                        PAYLOADS_ID,
                                                    ]
                                                ),
                                                "Data",
                                            ]
                                        ),
                                        ItemKey=VBindProp([VFOR_DATA, "@PromptIndex"]),
                                    ),
                                )
                            ]
                        ),
                        slots={
                            "icon": NormalComponent(Type="Close"),
                        },
                    ),
                ],
            },
        )


class UI_SinglePrompt(NFlex):
    def __init__(self):
        super().__init__(
            vertical=True,
            size=1,
            style={
                "border": "1px solid #555",
                "border-radius": "5px",
                "padding": "5px",
                "width": "95%",
            },
            slots={
                "default": [
                    UI_PromptOperate(),
                    NInput(
                        autosize=NInputAutoSize(minRows=3, maxRows=10),
                        type="textarea",
                        showCount=True,
                        value=VModelProp(
                            [
                                THIS_NODE_DATA,
                                "Payloads",
                                "ById",
                                VBindProp(
                                    [
                                        CONTEXT_FUNCTION,
                                        PAYLOADS_ID,
                                    ]
                                ),
                                "Data",
                                VBindProp([VFOR_DATA, "@PromptIndex"]),
                                "content",
                            ]
                        ),
                    ),
                ]
            },
        )


class UI_SinglePromptWrmbtn(NFlex):
    def __init__(self):
        super().__init__(
            vertical=False,
            wrap=False,
            justify="space-between",
            style={
                "align-content": "center",
                "align-items": "center",
            },
            slots={
                "default": [
                    UI_SinglePrompt(),
                    NButton(
                        style={"width": "5%"},
                        type="error",
                        size="small",
                        circle=True,
                        level="tertiary",
                        onClick=FunctionProp(
                            Funcs=[
                                REMOVEITEM_FuncProp(
                                    Arg=FuncArg_REMOVEITEM(
                                        DstPath=VBindProp(
                                            [
                                                THIS_NODE_DATA,
                                                "Payloads",
                                                "ById",
                                                VBindProp(
                                                    [
                                                        CONTEXT_FUNCTION,
                                                        PAYLOADS_ID,
                                                    ]
                                                ),
                                                "Data",
                                            ]
                                        ),
                                        ItemKey=VBindProp([VFOR_DATA, "@PromptIndex"]),
                                    ),
                                )
                            ]
                        ),
                        slots={
                            "icon": NormalComponent(Type="Close"),
                        },
                    ),
                ]
            },
        )


class UI_LLM_PROMPTS(NFlex):
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
                                Header(type="warning", text="Prompts设计"),
                                NButton(
                                    type="warning",
                                    text=True,
                                    onClick=FunctionProp(
                                        Funcs=[
                                            APPENDITEM_FuncProp(
                                                Arg=FuncArg_APPENDITEM(
                                                    DstPath=VBindProp(
                                                        [
                                                            THIS_NODE_DATA,
                                                            "Payloads",
                                                            "ById",
                                                            VBindProp(
                                                                [
                                                                    CONTEXT_FUNCTION,
                                                                    PAYLOADS_ID,
                                                                ]
                                                            ),
                                                            "Data",
                                                        ]
                                                    ),
                                                    ItemValue=DefaultPrompt,
                                                )
                                            )
                                        ]
                                    ),
                                    slots={
                                        "default": SpanComponent(ValueProp("添加")),
                                        "icon": NormalComponent(Type="Add"),
                                    },
                                ),
                            ]
                        },
                    ),
                    NFlex(
                        vertical=True,
                        size="small",
                        slots={
                            "default": ForLoopComponent(
                                Items=VBindProp(
                                    [
                                        THIS_NODE_DATA,
                                        "Payloads",
                                        "ById",
                                        VBindProp(
                                            [
                                                CONTEXT_FUNCTION,
                                                PAYLOADS_ID,
                                            ]
                                        ),
                                        "Data",
                                    ]
                                ),
                                ItemLabel="@Prompt",
                                IndexLabel="@PromptIndex",
                                Template=UI_SinglePromptWrmbtn(),
                            )
                        },
                    ),
                ],
            },
        )


EXPORT_UI = UI_LLM_PROMPTS

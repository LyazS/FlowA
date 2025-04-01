from typing import List, Dict, Union, Literal, Optional
from pydantic import BaseModel
from app.schemas.VFNodeInterface import VFNodeContentData
from app.uisdk import *
from ..UI_Components.Header import Header
from ..UI_Components.RefVarSelect import UI_RefVarSelect
from .LLM_inference import (
    LLMSettingType,
    LLMSetting,
    LLMTypeOptions,
    LLMTypeOptionsWnull,
    LLMRoleOptions,
    LLMRole,
    SinglePrompt,
)

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
                                Data=[
                                    THIS_NODE_DATA,
                                    "Payloads",
                                    "ById",
                                    PAYLOADS_ID,
                                    "Data",
                                    "@PromptIndex",
                                    "role",
                                ]
                            ),
                        },
                    ),
                    NButton(
                        style={"margin-bottom": 0},
                        type="warning",
                        text=True,
                        onClick=OPENEDITOR_FuncProp(
                            Arg=FuncArg_OPENEDITOR(
                                DstPath=[
                                    THIS_NODE_DATA,
                                    "Payloads",
                                    "ById",
                                    PAYLOADS_ID,
                                    "Data",
                                    "@PromptIndex",
                                    "content",
                                ],
                                Language="text",
                            )
                        ),
                        slots={
                            "default": SpanComponent(
                                Type=ComponentType.VALUE, Data="编辑"
                            ),
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
                            Data=[
                                THIS_NODE_DATA,
                                "Payloads",
                                "ById",
                                PAYLOADS_ID,
                                "Data",
                                "@PromptIndex",
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
                                        "@PromptIndex",
                                    ]
                                ),
                            ),
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
                            Data=[
                                THIS_NODE_DATA,
                                "Payloads",
                                "ById",
                                PAYLOADS_ID,
                                "Data",
                                "@PromptIndex",
                                "content",
                            ]
                        ),
                    ),
                ]
            },
        )
        pass


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
                                        "@PromptIndex",
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
                                    onClick=APPENDITEM_FuncProp(
                                        Arg=FuncArg_APPENDITEM(
                                            DstPath=[
                                                THIS_NODE_DATA,
                                                "Payloads",
                                                "ById",
                                                PAYLOADS_ID,
                                                "Data",
                                            ],
                                            ItemValue=DefaultPrompt,
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
                    NFlex(
                        vertical=True,
                        size="small",
                        slots={
                            "default": ForLoopComponent(
                                Items=VBindProp(
                                    Data=[
                                        THIS_NODE_DATA,
                                        "Payloads",
                                        "ById",
                                        PAYLOADS_ID,
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

from typing import List, Dict, Union, Literal, Optional
from pydantic import BaseModel
from app.schemas.VFNodeInterface import VFNodeContentData, VarType
from app.uisdk import *
from .LLM_inference import (
    LLMSettingType,
    LLMSetting,
    LLMTypeOptions,
    LLMTypeOptionsWnull,
    LLMRoleOptions,
    LLMRole,
    LLMPrompt,
    LLMPromptType,
    LLMPromptImageDetail,
    LLMPromptImageURL,
    LLMPromptTextParam,
    LLMPromptImageParam,
    LLMPromptImageParamType,
)
from ..UI_Components.Header import Header
from ..UI_Components.NInput import NInput, NInputAutoSize
from ..UI_Components.NButton import NButton
from ..UI_Components.NFlex import NFlex
from ..UI_Components.RefVarSelect import UI_RefVarSelect

DefaultPrompt = LLMPrompt(role=LLMRole.user, content=[LLMPromptTextParam(text="")])


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
                                            COMPONENT_CONTEXT,
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
                    NormalComponent(
                        Type="NDropdown",
                        Props={
                            "trigger": "hover",
                            "options": [
                                {
                                    "label": "添加图像",
                                    "key": "refimage",
                                    "props": {
                                        "onClick": OperateFunctionProp(
                                            [
                                                APPENDITEM_FuncProp(
                                                    Arg=FuncArg_APPENDITEM(
                                                        Position=InsertPos.Start,
                                                        DstPath=VBindProp(
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
                                                                VBindProp(
                                                                    [
                                                                        VFOR_DATA,
                                                                        "@PromptIndex",
                                                                    ]
                                                                ),
                                                                "content",
                                                            ]
                                                        ),
                                                        ItemValue=LLMPromptImageParam(
                                                            image_url=LLMPromptImageURL(
                                                                detail=LLMPromptImageDetail.auto,
                                                                urlType=LLMPromptImageParamType.FromRef,
                                                            )
                                                        ),
                                                    )
                                                )
                                            ]
                                        )
                                    },
                                },
                                {
                                    "label": "上传图像",
                                    "key": "uploadimage",
                                    "props": {
                                        "onClick": OperateFunctionProp(
                                            [
                                                APPENDITEM_FuncProp(
                                                    Arg=FuncArg_APPENDITEM(
                                                        Position=InsertPos.Start,
                                                        DstPath=VBindProp(
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
                                                                VBindProp(
                                                                    [
                                                                        VFOR_DATA,
                                                                        "@PromptIndex",
                                                                    ]
                                                                ),
                                                                "content",
                                                            ]
                                                        ),
                                                        ItemValue=LLMPromptImageParam(
                                                            image_url=LLMPromptImageURL(
                                                                detail=LLMPromptImageDetail.auto,
                                                                urlType=LLMPromptImageParamType.FromUpload,
                                                                url=AsyncReturnFunctionProp(
                                                                    UPLOADFILE_FuncProp(
                                                                        Arg=FuncArg_UPLOADFILE(
                                                                            FileType=UploadFileInfoType.URL,
                                                                            FilterType=[
                                                                                "image/*"
                                                                            ],
                                                                        )
                                                                    )
                                                                ),
                                                            )
                                                        ),
                                                    )
                                                )
                                            ]
                                        )
                                    },
                                },
                                {
                                    "label": "添加文本",
                                    "key": "addtext",
                                    "props": {
                                        "onClick": OperateFunctionProp(
                                            [
                                                APPENDITEM_FuncProp(
                                                    Arg=FuncArg_APPENDITEM(
                                                        DstPath=VBindProp(
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
                                                                VBindProp(
                                                                    [
                                                                        VFOR_DATA,
                                                                        "@PromptIndex",
                                                                    ]
                                                                ),
                                                                "content",
                                                            ]
                                                        ),
                                                        ItemValue=LLMPromptTextParam(
                                                            text=""
                                                        ),
                                                    )
                                                )
                                            ]
                                        )
                                    },
                                },
                            ],
                        },
                        Slots={
                            "default": NButton(
                                type="warning",
                                level="quaternary",
                                round=True,
                                slots={
                                    "icon": NormalComponent(Type="Add"),
                                },
                            ),
                        },
                    ),
                ]
            },
        )


class UI_Prompt_Image_Ref(NFlex):
    def __init__(self):
        super().__init__(
            vertical=False,
            wrap=False,
            justify="flex-end",
            style={
                "width": "100%",
                "align-content": "center",
                "align-items": "center",
                "border": "1px solid #555",
                "border-radius": "5px",
                "padding": "3px",
            },
            slots={
                "default": [
                    UI_RefVarSelect(
                        size="tiny",
                        style={"width": "60%"},
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
                                VBindProp([VFOR_DATA, "@PromptIndex"]),
                                "content",
                                VBindProp([VFOR_DATA, "@PromptItemIndex"]),
                                "image_url",
                                "urlRef",
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
                                VarType.Image,
                            ]
                        ),
                    ),
                    NormalComponent(
                        Type="NSelect",
                        Props={
                            "width": "19%",
                            "size": "tiny",
                            "menu-size": "tiny",
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
                                    VBindProp([VFOR_DATA, "@PromptIndex"]),
                                    "content",
                                    VBindProp([VFOR_DATA, "@PromptItemIndex"]),
                                    "image_url",
                                    "detail",
                                ]
                            ),
                            "options": [
                                SelectOptions(
                                    label="AUTO",
                                    value=LLMPromptImageDetail.auto,
                                ),
                                SelectOptions(
                                    label="LOW",
                                    value=LLMPromptImageDetail.low,
                                ),
                                SelectOptions(
                                    label="HIGH",
                                    value=LLMPromptImageDetail.high,
                                ),
                            ],
                        },
                    ),
                    NButton(
                        round=True,
                        type="error",
                        level="tertiary",
                        size="tiny",
                        style={"width": "19%"},
                        onClick=OperateFunctionProp(
                            [
                                REMOVEITEM_FuncProp(
                                    Arg=FuncArg_REMOVEITEM(
                                        DstPath=VBindProp(
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
                                                VBindProp(
                                                    [
                                                        VFOR_DATA,
                                                        "@PromptIndex",
                                                    ]
                                                ),
                                                "content",
                                            ]
                                        ),
                                        ItemKey=VBindProp(
                                            [VFOR_DATA, "@PromptItemIndex"]
                                        ),
                                    )
                                )
                            ]
                        ),
                        slots={"default": SpanComponent(ValueProp("删除"))},
                    ),
                ]
            },
            IfCondition=LogicalCondition(
                Operator="AND",
                Conditions=[
                    CompareCondition(
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
                                VBindProp([VFOR_DATA, "@PromptIndex"]),
                                "content",
                                VBindProp([VFOR_DATA, "@PromptItemIndex"]),
                                "type",
                            ]
                        ),
                        Operator="==",
                        Right=ValueProp(LLMPromptType.image_url),
                    ),
                    CompareCondition(
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
                                VBindProp([VFOR_DATA, "@PromptIndex"]),
                                "content",
                                VBindProp([VFOR_DATA, "@PromptItemIndex"]),
                                "image_url",
                                "urlType",
                            ]
                        ),
                        Operator="==",
                        Right=ValueProp(LLMPromptImageParamType.FromRef),
                    ),
                ],
            ),
        )


class UI_Prompt_Image_Upload(NFlex):
    def __init__(self):
        super().__init__(
            vertical=False,
            wrap=False,
            justify="flex-start",
            style={
                "align-content": "center",
                "align-items": "center",
                "border": "1px solid #555",
                "border-radius": "5px",
                "padding": "3px",
            },
            slots={
                "default": [
                    NormalComponent(
                        Type="NImage",
                        Props={
                            "height": "100px",
                            "width": "100px",
                            "object-fit": "cover",
                            "src": ReturnFunctionProp(
                                FORMATSTRING_FuncProp(
                                    Arg=FuncArg_FORMATSTRING(
                                        FString="{{backendurl}}/file/get/{{imgurl}}",
                                        Args={
                                            "backendurl": ReturnFunctionProp(
                                                BACKENDURL_FuncProp()
                                            ),
                                            "imgurl": VBindProp(
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
                                                    VBindProp(
                                                        [VFOR_DATA, "@PromptIndex"]
                                                    ),
                                                    "content",
                                                    VBindProp(
                                                        [VFOR_DATA, "@PromptItemIndex"]
                                                    ),
                                                    "image_url",
                                                    "url",
                                                    "File",
                                                ]
                                            ),
                                        },
                                    )
                                )
                            ),
                        },
                    ),
                    NFlex(
                        vertical=True,
                        slots={
                            "default": [
                                NormalComponent(
                                    Type="NSelect",
                                    Props={
                                        "size": "tiny",
                                        "menu-size": "tiny",
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
                                                VBindProp([VFOR_DATA, "@PromptIndex"]),
                                                "content",
                                                VBindProp(
                                                    [VFOR_DATA, "@PromptItemIndex"]
                                                ),
                                                "image_url",
                                                "detail",
                                            ]
                                        ),
                                        "options": [
                                            SelectOptions(
                                                label="AUTO",
                                                value=LLMPromptImageDetail.auto,
                                            ),
                                            SelectOptions(
                                                label="LOW",
                                                value=LLMPromptImageDetail.low,
                                            ),
                                            SelectOptions(
                                                label="HIGH",
                                                value=LLMPromptImageDetail.high,
                                            ),
                                        ],
                                    },
                                ),
                                NButton(
                                    round=True,
                                    type="error",
                                    level="tertiary",
                                    size="tiny",
                                    onClick=OperateFunctionProp(
                                        [
                                            DELETEIMAGE_FuncProp(
                                                Arg=FuncArg_DELETEIMAGE(
                                                    Filename=VBindProp(
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
                                                            VBindProp(
                                                                [
                                                                    VFOR_DATA,
                                                                    "@PromptIndex",
                                                                ]
                                                            ),
                                                            "content",
                                                            VBindProp(
                                                                [
                                                                    VFOR_DATA,
                                                                    "@PromptItemIndex",
                                                                ]
                                                            ),
                                                            "image_url",
                                                            "url",
                                                            "File",
                                                        ]
                                                    ),
                                                )
                                            ),
                                            REMOVEITEM_FuncProp(
                                                Arg=FuncArg_REMOVEITEM(
                                                    DstPath=VBindProp(
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
                                                            VBindProp(
                                                                [
                                                                    VFOR_DATA,
                                                                    "@PromptIndex",
                                                                ]
                                                            ),
                                                            "content",
                                                        ]
                                                    ),
                                                    ItemKey=VBindProp(
                                                        [VFOR_DATA, "@PromptItemIndex"]
                                                    ),
                                                )
                                            ),
                                        ]
                                    ),
                                    slots={"default": SpanComponent(ValueProp("删除"))},
                                ),
                            ]
                        },
                    ),
                ]
            },
            IfCondition=LogicalCondition(
                Operator="AND",
                Conditions=[
                    CompareCondition(
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
                                VBindProp([VFOR_DATA, "@PromptIndex"]),
                                "content",
                                VBindProp([VFOR_DATA, "@PromptItemIndex"]),
                                "type",
                            ]
                        ),
                        Operator="==",
                        Right=ValueProp(LLMPromptType.image_url),
                    ),
                    CompareCondition(
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
                                VBindProp([VFOR_DATA, "@PromptIndex"]),
                                "content",
                                VBindProp([VFOR_DATA, "@PromptItemIndex"]),
                                "image_url",
                                "urlType",
                            ]
                        ),
                        Operator="==",
                        Right=ValueProp(LLMPromptImageParamType.FromUpload),
                    ),
                ],
            ),
        )


class UI_Prompt_Text_Input(NFlex):
    def __init__(self):
        super().__init__(
            vertical=False,
            wrap=False,
            justify="flex-start",
            style={
                "width": "100%",
                "align-content": "center",
                "align-items": "center",
                "border": "1px solid #555",
                "border-radius": "5px",
                "padding": "3px",
            },
            slots={
                "default": [
                    NInput(
                        type="textarea",
                        showCount=True,
                        autosize=NInputAutoSize(minRows=3, maxRows=15),
                        style={"width": "90%"},
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
                                VBindProp([VFOR_DATA, "@PromptIndex"]),
                                "content",
                                VBindProp([VFOR_DATA, "@PromptItemIndex"]),
                                "text",
                            ]
                        ),
                    ),
                    NFlex(
                        vertical=True,
                        style={"width": "10%"},
                        slots={
                            "default": [
                                NButton(
                                    round=True,
                                    type="warning",
                                    level="tertiary",
                                    size="tiny",
                                    onClick=OperateFunctionProp(
                                        [
                                            OPENEDITOR_FuncProp(
                                                Arg=FuncArg_OPENEDITOR(
                                                    DstPath=VBindProp(
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
                                                            VBindProp(
                                                                [
                                                                    VFOR_DATA,
                                                                    "@PromptIndex",
                                                                ]
                                                            ),
                                                            "content",
                                                            VBindProp(
                                                                [
                                                                    VFOR_DATA,
                                                                    "@PromptItemIndex",
                                                                ]
                                                            ),
                                                            "text",
                                                        ]
                                                    ),
                                                    Language="text",
                                                )
                                            )
                                        ]
                                    ),
                                    slots={"default": SpanComponent(ValueProp("编辑"))},
                                ),
                                NButton(
                                    round=True,
                                    type="error",
                                    level="tertiary",
                                    size="tiny",
                                    onClick=OperateFunctionProp(
                                        [
                                            REMOVEITEM_FuncProp(
                                                Arg=FuncArg_REMOVEITEM(
                                                    DstPath=VBindProp(
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
                                                            VBindProp(
                                                                [
                                                                    VFOR_DATA,
                                                                    "@PromptIndex",
                                                                ]
                                                            ),
                                                            "content",
                                                        ]
                                                    ),
                                                    ItemKey=VBindProp(
                                                        [VFOR_DATA, "@PromptItemIndex"]
                                                    ),
                                                )
                                            )
                                        ]
                                    ),
                                    slots={"default": SpanComponent(ValueProp("删除"))},
                                ),
                            ]
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
                        VBindProp([VFOR_DATA, "@PromptIndex"]),
                        "content",
                        VBindProp([VFOR_DATA, "@PromptItemIndex"]),
                        "type",
                    ]
                ),
                Operator="==",
                Right=ValueProp(LLMPromptType.text),
            ),
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
                    NFlex(
                        vertical=False,
                        justify="flex-start",
                        style={
                            "width": "100%",
                            "align-content": "center",
                            "align-items": "center",
                        },
                        slots={
                            "default": ForLoopComponent(
                                Items=VBindProp(
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
                                        VBindProp([VFOR_DATA, "@PromptIndex"]),
                                        "content",
                                    ]
                                ),
                                ItemLabel="@PromptItem",
                                IndexLabel="@PromptItemIndex",
                                Template=[
                                    UI_Prompt_Image_Ref(),
                                    UI_Prompt_Image_Upload(),
                                    UI_Prompt_Text_Input(),
                                ],
                            ),
                        },
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
                        onClick=OperateFunctionProp(
                            [
                                REMOVEITEM_FuncProp(
                                    Arg=FuncArg_REMOVEITEM(
                                        DstPath=VBindProp(
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
                                    onClick=OperateFunctionProp(
                                        [
                                            APPENDITEM_FuncProp(
                                                Arg=FuncArg_APPENDITEM(
                                                    DstPath=VBindProp(
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
                                                COMPONENT_CONTEXT,
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
"""
两种
1. 上传，传给image_url就是b64str
2. 引用，传给image_url就是RefVarItem
    引用的如果是Image就转成b64
    如果是str就直接用
"""

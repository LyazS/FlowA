from typing import List, Dict, Union, Literal, Optional
from pydantic import BaseModel
from app.schemas.VFNodeInterface import VFNodeContentData, VarType
from app.uisdk import *

from ..UI_Components.Header import Header
from ..UI_Components.NInput import NInput, NInputAutoSize
from ..UI_Components.NButton import NButton
from ..UI_Components.NFlex import NFlex
from .http_request import (
    HttpRequestMethod,
    HttpRequestBodyType,
    HttpRequestBody_XWWWFORMURL,
    HttpRequestBody_FORMDATA,
    HttpRequestConfig_BODY,
)


class content1_body(NInput):
    def __init__(self):
        super().__init__(
            autosize=NInputAutoSize(minRows=3, maxRows=15),
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
                    "Content1",
                ]
            ),
            IfCondition=LogicalCondition(
                Operator="OR",
                Conditions=[
                    CompareCondition(
                        Left=VBindProp(
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
                                "Type",
                            ]
                        ),
                        Operator="==",
                        Right=ValueProp(HttpRequestBodyType.TEXT),
                    ),
                    CompareCondition(
                        Left=VBindProp(
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
                                "Type",
                            ]
                        ),
                        Operator="==",
                        Right=ValueProp(HttpRequestBodyType.JSON),
                    ),
                ],
            ),
        )


class content2_body(NFlex):
    def __init__(self):
        super().__init__(
            IfCondition=CompareCondition(
                Left=VBindProp(
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
                        "Type",
                    ]
                ),
                Operator="==",
                Right=ValueProp(HttpRequestBodyType.XWWWFORMURL),
            ),
            vertical=True,
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
                            "Content2",
                        ]
                    ),
                    ItemLabel="@XWWWFORMURLItem",
                    IndexLabel="@XWWWFORMURLIndex",
                    Template=NFlex(
                        vertical=False,
                        wrap=False,
                        justify="space-between",
                        style={
                            "align-content": "center",
                            "align-items": "center",
                        },
                        slots={
                            "default": [
                                NFlex(
                                    vertical=False,
                                    wrap=False,
                                    justify="space-between",
                                    style={
                                        "align-content": "center",
                                        "align-items": "center",
                                        "width": "95%",
                                    },
                                    slots={
                                        "default": [
                                            NInput(
                                                style={"width": "50%"},
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
                                                        "Content2",
                                                        VBindProp(
                                                            [
                                                                VFOR_DATA,
                                                                "@XWWWFORMURLIndex",
                                                            ]
                                                        ),
                                                        "Key",
                                                    ]
                                                ),
                                            ),
                                            NInput(
                                                style={"width": "50%"},
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
                                                        "Content2",
                                                        VBindProp(
                                                            [
                                                                VFOR_DATA,
                                                                "@XWWWFORMURLIndex",
                                                            ]
                                                        ),
                                                        "Value",
                                                    ]
                                                ),
                                            ),
                                        ]
                                    },
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
                                                            "Content2",
                                                        ]
                                                    ),
                                                    ItemKey=VBindProp(
                                                        [
                                                            VFOR_DATA,
                                                            "@XWWWFORMURLIndex",
                                                        ]
                                                    ),
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
                    ),
                )
            },
        )


class content3_body(NFlex):
    def __init__(self):
        super().__init__(
            IfCondition=CompareCondition(
                Left=VBindProp(
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
                        "Type",
                    ]
                ),
                Operator="==",
                Right=ValueProp(HttpRequestBodyType.FORMDATA),
            ),
            vertical=True,
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
                            "Content3",
                        ]
                    ),
                    ItemLabel="@FORMDATAItem",
                    IndexLabel="@FORMDATAIndex",
                    Template=NFlex(
                        vertical=False,
                        wrap=False,
                        justify="space-between",
                        style={
                            "align-content": "center",
                            "align-items": "center",
                        },
                        slots={
                            "default": [
                                NFlex(
                                    vertical=False,
                                    wrap=False,
                                    justify="space-between",
                                    style={
                                        "align-content": "center",
                                        "align-items": "center",
                                        "width": "95%",
                                    },
                                    slots={
                                        "default": [
                                            NInput(
                                                style={"width": "40%"},
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
                                                        "Content3",
                                                        VBindProp(
                                                            [
                                                                VFOR_DATA,
                                                                "@FORMDATAIndex",
                                                            ]
                                                        ),
                                                        "Key",
                                                    ]
                                                ),
                                            ),
                                            NormalComponent(
                                                Type="NSelect",
                                                Props={
                                                    "style": {"width": "20%"},
                                                    "size": "small",
                                                    "consistent-menu-width": False,
                                                    "options": [
                                                        {
                                                            "label": "字符串",
                                                            "value": VarType.String,
                                                        },
                                                        {
                                                            "label": "文件",
                                                            "value": VarType.File,
                                                        },
                                                    ],
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
                                                            "Content3",
                                                            VBindProp(
                                                                [
                                                                    VFOR_DATA,
                                                                    "@FORMDATAIndex",
                                                                ]
                                                            ),
                                                            "Type",
                                                        ]
                                                    ),
                                                },
                                            ),
                                            NInput(
                                                style={"width": "40%"},
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
                                                        "Content3",
                                                        VBindProp(
                                                            [
                                                                VFOR_DATA,
                                                                "@FORMDATAIndex",
                                                            ]
                                                        ),
                                                        "Value",
                                                    ]
                                                ),
                                            ),
                                        ]
                                    },
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
                                                            "Content3",
                                                        ]
                                                    ),
                                                    ItemKey=VBindProp(
                                                        [
                                                            VFOR_DATA,
                                                            "@FORMDATAIndex",
                                                        ]
                                                    ),
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
                    ),
                )
            },
        )


class http_content1_text_btn(NButton):
    def __init__(self):
        super().__init__(
            IfCondition=CompareCondition(
                Left=VBindProp(
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
                        "Type",
                    ]
                ),
                Operator="==",
                Right=ValueProp(HttpRequestBodyType.TEXT),
            ),
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
                                    "Content1",
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
        )


class http_content1_json_btn(NButton):
    def __init__(self):
        super().__init__(
            IfCondition=CompareCondition(
                Left=VBindProp(
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
                        "Type",
                    ]
                ),
                Operator="==",
                Right=ValueProp(HttpRequestBodyType.JSON),
            ),
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
                                    "Content1",
                                ]
                            ),
                            Language="json",
                        )
                    )
                ]
            ),
            slots={
                "default": SpanComponent(ValueProp("编辑")),
                "icon": NormalComponent(Type="CreateOutline"),
            },
        )


class http_content2_btn(NButton):
    def __init__(self):
        super().__init__(
            IfCondition=CompareCondition(
                Left=VBindProp(
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
                        "Type",
                    ]
                ),
                Operator="==",
                Right=ValueProp(HttpRequestBodyType.XWWWFORMURL),
            ),
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
                                    "Content2",
                                ]
                            ),
                            ItemValue=HttpRequestBody_XWWWFORMURL(Key="", Value=""),
                        )
                    )
                ]
            ),
            slots={
                "default": SpanComponent(ValueProp("新增")),
                "icon": NormalComponent(Type="Add"),
            },
        )


class http_content3_btn(NButton):
    def __init__(self):
        super().__init__(
            IfCondition=CompareCondition(
                Left=VBindProp(
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
                        "Type",
                    ]
                ),
                Operator="==",
                Right=ValueProp(HttpRequestBodyType.FORMDATA),
            ),
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
                                    "Content3",
                                ]
                            ),
                            ItemValue=HttpRequestBody_FORMDATA(
                                Key="", Value="", Type=VarType.String
                            ),
                        )
                    )
                ]
            ),
            slots={
                "default": SpanComponent(ValueProp("新增")),
                "icon": NormalComponent(Type="Add"),
            },
        )


class http_type_btn(NFlex):
    def __init__(self):
        super().__init__(
            vertical=False,
            wrap=False,
            justify="flex-end",
            style={"align-content": "center", "align-items": "center"},
            slots={
                "default": [
                    http_content1_text_btn(),
                    http_content1_json_btn(),
                    http_content2_btn(),
                    http_content3_btn(),
                    NormalComponent(
                        Type="NSelect",
                        Props={
                            "size": "medium",
                            "style": {"width": "10em"},
                            "options": [
                                {
                                    "label": "无",
                                    "value": HttpRequestBodyType.NONE,
                                },
                                {
                                    "label": "JSON",
                                    "value": HttpRequestBodyType.JSON,
                                },
                                {
                                    "label": "TEXT",
                                    "value": HttpRequestBodyType.TEXT,
                                },
                                {
                                    "label": "FORMDATA",
                                    "value": HttpRequestBodyType.FORMDATA,
                                },
                                {
                                    "label": "XWWWFORMURL",
                                    "value": HttpRequestBodyType.XWWWFORMURL,
                                },
                            ],
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
                                    "Type",
                                ]
                            ),
                        },
                    ),
                ]
            },
        )


class UI_http_body(NFlex):
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
                                Header(
                                    type="warning",
                                    text=VBindProp(
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
                                            "Label",
                                        ]
                                    ),
                                ),
                                http_type_btn(),
                            ]
                        },
                    ),
                    content1_body(),
                    content2_body(),
                    content3_body(),
                ],
            },
        )


EXPORT_UI = UI_http_body

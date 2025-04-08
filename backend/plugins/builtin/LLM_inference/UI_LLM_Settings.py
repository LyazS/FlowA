from typing import List, Dict, Union, Literal, Optional
from pydantic import BaseModel
from app.schemas.VFNodeInterface import VFNodeContentData
from app.uisdk import *
from .LLM_inference import (
    LLMSettingType,
    LLMSetting,
    LLMTypeOptions,
    LLMTypeOptionsWnull,
)
from app.schemas.VFNodeInterface import VFNodeConnectionType
from ..UI_Components.Header import Header
from ..UI_Components.RefVarSelect import UI_RefVarSelect
from ..UI_Components.NSwitch import NSwitch
from ..UI_Components.NFlex import NFlex


class SingleAttrBoolean(NFlex):
    def __init__(
        self,
        attr_path: List[Union[str, int]],
        typeOptions: List[SelectOptions],
    ):
        super().__init__(
            vertical=False,
            wrap=False,
            style={"align-content": "center", "align-items": "center"},
            slots={
                "default": [
                    # 标签 ====================================================
                    NormalComponent(
                        Type="NTag",
                        Props={
                            "type": "info",
                            "bordered": False,
                            "size": "small",
                            "style": {"width": "5em"},
                        },
                        Slots={
                            "default": SpanComponent(
                                Type=ComponentType.VBIND,
                                Data=attr_path + ["Label"],
                            )
                        },
                    ),
                    # 类型选择 =================================================
                    NormalComponent(
                        Type="NSelect",
                        Props={
                            "size": "tiny",
                            "consistent-menu-width": False,
                            "style": {"width": "5em"},
                            "options": typeOptions,
                            "value": VModelProp(Data=attr_path + ["Type"]),
                        },
                    ),
                    # 值输入框 =================================================
                    UI_RefVarSelect(
                        value=VModelProp(Data=attr_path + ["Content"]),
                        size="tiny",
                        options=VBindProp(
                            Data=[
                                CONNECT_DATA_TO_SELECT,
                                VFNodeConnectionType.Self,
                                "self",
                            ]
                        ),
                        IfCondition=CompareCondition(
                            Left=VBindProp(Data=attr_path + ["Type"]),
                            Operator="==",
                            Right=ValueProp(Data=LLMSettingType.Ref),
                        ),
                    ),
                    NSwitch(
                        size="small",
                        value=VModelProp(Data=attr_path + ["Content"]),
                        IfCondition=CompareCondition(
                            Left=VBindProp(Data=attr_path + ["Type"]),
                            Operator="==",
                            Right=ValueProp(Data=LLMSettingType.Const),
                        ),
                    ),
                ]
            },
        )

    pass


class SingleAttrNumber(NFlex):
    def __init__(
        self,
        attr_path: List[Union[str, int]],
        typeOptions: List[SelectOptions],
        min: Optional[float] = None,
        max: Optional[float] = None,
        step: Optional[float] = None,
        precision: Optional[int] = None,
    ):
        super().__init__(
            vertical=False,
            wrap=False,
            style={"align-content": "center", "align-items": "center"},
            slots={
                "default": [
                    # 标签 ====================================================
                    NormalComponent(
                        Type="NTag",
                        Props={
                            "type": "info",
                            "bordered": False,
                            "size": "small",
                            "style": {"width": "5em"},
                        },
                        Slots={
                            "default": SpanComponent(
                                Type=ComponentType.VBIND,
                                Data=attr_path + ["Label"],
                            )
                        },
                    ),
                    # 类型选择 =================================================
                    NormalComponent(
                        Type="NSelect",
                        Props={
                            "size": "tiny",
                            "consistent-menu-width": False,
                            "style": {"width": "5em"},
                            "options": typeOptions,
                            "value": VModelProp(Data=attr_path + ["Type"]),
                        },
                    ),
                    # 值输入框 =================================================
                    UI_RefVarSelect(
                        value=VModelProp(Data=attr_path + ["Content"]),
                        size="tiny",
                        options=VBindProp(
                            Data=[
                                CONNECT_DATA_TO_SELECT,
                                VFNodeConnectionType.Self,
                                "self",
                            ]
                        ),
                        IfCondition=CompareCondition(
                            Left=VBindProp(Data=attr_path + ["Type"]),
                            Operator="==",
                            Right=ValueProp(Data=LLMSettingType.Ref),
                        ),
                    ),
                    NormalComponent(
                        Type="NInputNumber",
                        Props={
                            "size": "tiny",
                            "min": min,
                            "max": max,
                            "step": step,
                            "precision": precision,
                            "value": VModelProp(Data=attr_path + ["Content"]),
                        },
                        IfCondition=CompareCondition(
                            Left=VBindProp(Data=attr_path + ["Type"]),
                            Operator="==",
                            Right=ValueProp(Data=LLMSettingType.Const),
                        ),
                    ),
                ]
            },
        )

    pass


class SingleAttrSelect(NFlex):
    def __init__(
        self,
        attr_path: List[Union[str, int]],
        typeOptions: List[SelectOptions],
        options: ReadOnlyPropVar,
    ):
        super().__init__(
            vertical=False,
            wrap=False,
            style={"align-content": "center", "align-items": "center"},
            slots={
                "default": [
                    # 标签 ====================================================
                    NormalComponent(
                        Type="NTag",
                        Props={
                            "type": "info",
                            "bordered": False,
                            "size": "small",
                            "style": {"width": "5em"},
                        },
                        Slots={
                            "default": SpanComponent(
                                Type=ComponentType.VBIND,
                                Data=attr_path + ["Label"],
                            )
                        },
                    ),
                    # 类型选择 =================================================
                    NormalComponent(
                        Type="NSelect",
                        Props={
                            "size": "tiny",
                            "consistent-menu-width": False,
                            "style": {"width": "5em"},
                            "options": typeOptions,
                            "value": VModelProp(Data=attr_path + ["Type"]),
                        },
                    ),
                    # 值输入框 =================================================
                    UI_RefVarSelect(
                        value=VModelProp(Data=attr_path + ["Content"]),
                        size="tiny",
                        options=VBindProp(
                            Data=[
                                CONNECT_DATA_TO_SELECT,
                                VFNodeConnectionType.Self,
                                "self",
                            ]
                        ),
                        IfCondition=CompareCondition(
                            Left=VBindProp(Data=attr_path + ["Type"]),
                            Operator="==",
                            Right=ValueProp(Data=LLMSettingType.Ref),
                        ),
                    ),
                    NormalComponent(
                        Type="NSelect",
                        Props={
                            "size": "tiny",
                            "consistent-menu-width": False,
                            "options": options,
                            "value": VModelProp(Data=attr_path + ["Content"]),
                        },
                        IfCondition=CompareCondition(
                            Left=VBindProp(Data=attr_path + ["Type"]),
                            Operator="==",
                            Right=ValueProp(Data=LLMSettingType.Const),
                        ),
                    ),
                ]
            },
        )

    pass


class UI_LLM_ATTRIBUTE_TAG(NFlex):
    def __init__(self):
        super().__init__(
            vertical=True,
            slots={
                "default": [
                    Header(type="success", text="模型设置"),
                    SingleAttrSelect(
                        attr_path=[
                            THIS_NODE_DATA,
                            "Payloads",
                            "ById",
                            PAYLOADS_ID,
                            "Data",
                            "Model",
                        ],
                        typeOptions=LLMTypeOptions,
                        options=VBindProp(
                            Data=[
                                NODE_CONFIG_DATA,
                                "models_select",
                            ],
                        ),
                    ),
                    SingleAttrBoolean(
                        attr_path=[
                            THIS_NODE_DATA,
                            "Payloads",
                            "ById",
                            PAYLOADS_ID,
                            "Data",
                            "Stream",
                        ],
                        typeOptions=LLMTypeOptionsWnull,
                    ),
                    SingleAttrNumber(
                        attr_path=[
                            THIS_NODE_DATA,
                            "Payloads",
                            "ById",
                            PAYLOADS_ID,
                            "Data",
                            "MaxTokens",
                        ],
                        typeOptions=LLMTypeOptionsWnull,
                        min=1,
                        step=1,
                        precision=0,
                    ),
                    SingleAttrNumber(
                        attr_path=[
                            THIS_NODE_DATA,
                            "Payloads",
                            "ById",
                            PAYLOADS_ID,
                            "Data",
                            "Temperature",
                        ],
                        typeOptions=LLMTypeOptionsWnull,
                        min=0.0,
                        max=1.5,
                        step=0.1,
                        precision=2,
                    ),
                    SingleAttrNumber(
                        attr_path=[
                            THIS_NODE_DATA,
                            "Payloads",
                            "ById",
                            PAYLOADS_ID,
                            "Data",
                            "TopP",
                        ],
                        typeOptions=LLMTypeOptionsWnull,
                        min=0.0,
                        max=1.0,
                        step=0.1,
                        precision=2,
                    ),
                    SingleAttrNumber(
                        attr_path=[
                            THIS_NODE_DATA,
                            "Payloads",
                            "ById",
                            PAYLOADS_ID,
                            "Data",
                            "FrequencyPenalty",
                        ],
                        typeOptions=LLMTypeOptionsWnull,
                        min=0.0,
                        max=1.0,
                        step=0.1,
                        precision=2,
                    ),
                    SingleAttrSelect(
                        attr_path=[
                            THIS_NODE_DATA,
                            "Payloads",
                            "ById",
                            PAYLOADS_ID,
                            "Data",
                            "ResponseFormat",
                        ],
                        typeOptions=LLMTypeOptionsWnull,
                        options=ValueProp(
                            Data=[
                                SelectOptions(label="text", value="text"),
                                SelectOptions(label="json", value="json"),
                            ],
                        ),
                    ),
                ]
            },
        )


EXPORT_UI = UI_LLM_ATTRIBUTE_TAG

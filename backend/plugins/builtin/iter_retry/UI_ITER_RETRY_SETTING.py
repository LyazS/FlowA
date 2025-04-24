from typing import List, Dict, Union, Literal, Any, Optional
from pydantic import BaseModel
from app.uisdk import *
from app.schemas.VFNodeInterface import VFNodeConnectionType
from ..UI_Components.Header import Header
from ..UI_Components.RefVarSelect import UI_RefVarSelect
from ..UI_Components.NFlex import NFlex
from .iter_retry import RetryType


class retry_type(NFlex):
    def __init__(self):
        super().__init__(
            vertical=False,
            wrap=False,
            justify="flex-start",
            style={"align-content": "center", "align-items": "center"},
            slots={
                "default": [
                    # 标签 ====================================================
                    NormalComponent(
                        Type="NTag",
                        Props={
                            "type": "info",
                            "bordered": False,
                            "size": "medium",
                            "style": {"width": "5em"},
                        },
                        Slots={"default": SpanComponent(ValueProp("重试类型"))},
                    ),
                    NormalComponent(
                        Type="NSelect",
                        Props={
                            "size": "small",
                            "consistent-menu-width": False,
                            "options": ValueProp(
                                [
                                    SelectOptions(
                                        label="立即重试", value=RetryType.Immediate
                                    ),
                                    SelectOptions(
                                        label="延迟重试", value=RetryType.Delay
                                    ),
                                    SelectOptions(
                                        label="指数重试", value=RetryType.Exponential
                                    ),
                                ],
                            ),
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
                                ],
                            ),
                        },
                    ),
                ]
            },
        )

    pass


class retry_num(NFlex):
    def __init__(
        self,
        label: str,
        contentPath: str,
        min: Optional[float] = None,
        max: Optional[float] = None,
        step: Optional[float] = None,
        precision: Optional[int] = None,
        IfCondition: Optional[Condition] = None,
    ):
        super().__init__(
            vertical=False,
            wrap=False,
            justify="flex-start",
            style={"align-content": "center", "align-items": "center"},
            slots={
                "default": [
                    NormalComponent(
                        Type="NTag",
                        Props={
                            "type": "info",
                            "bordered": False,
                            "size": "medium",
                            "style": {"width": "5em"},
                        },
                        Slots={"default": SpanComponent(ValueProp(label))},
                    ),
                    NormalComponent(
                        Type="NInputNumber",
                        Props={
                            "size": "small",
                            "min": min,
                            "max": max,
                            "step": step,
                            "precision": precision,
                            "value": VModelProp(
                                Data=[
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
                                    contentPath,
                                ]
                            ),
                        },
                    ),
                ]
            },
            IfCondition=IfCondition,
        )

    pass


class UI_ITER_RETRY_SETTING(NFlex):
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
                                        CONTEXT_FUNCTION,
                                        PAYLOADS_ID,
                                    ]
                                ),
                                "Label",
                            ]
                        ),
                    ),
                    retry_type(),
                    retry_num(
                        label="重试次数",
                        contentPath="Num",
                        min=1,
                        step=1,
                        precision=0,
                    ),
                    retry_num(
                        label="延迟时间",
                        contentPath="Delay",
                        min=0.0,
                        step=1.0,
                        precision=2,
                        IfCondition=LogicalCondition(
                            Type=ConditionType.Logical,
                            Operator="OR",
                            Conditions=[
                                CompareCondition(
                                    Type=ConditionType.Compare,
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
                                    Right=ValueProp(RetryType.Delay),
                                ),
                                CompareCondition(
                                    Type=ConditionType.Compare,
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
                                    Right=ValueProp(RetryType.Exponential),
                                ),
                            ],
                        ),
                    ),
                    retry_num(
                        label="指数因子",
                        contentPath="ExpBase",
                        min=1.0,
                        step=1.0,
                        precision=2,
                        IfCondition=CompareCondition(
                            Type=ConditionType.Compare,
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
                            Right=ValueProp(RetryType.Exponential),
                        ),
                    ),
                    retry_num(
                        label="指数增长",
                        contentPath="ExpFactor",
                        min=1.0,
                        step=1.0,
                        precision=2,
                        IfCondition=CompareCondition(
                            Type=ConditionType.Compare,
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
                            Right=ValueProp(RetryType.Exponential),
                        ),
                    ),
                ],
            },
        )


EXPORT_UI = UI_ITER_RETRY_SETTING

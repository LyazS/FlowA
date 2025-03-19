from typing import List, Dict, Any, Optional
from pydantic import BaseModel, field_validator, ValidationInfo
from enum import StrEnum

"""
Type 指向组件的类型，例如NInput，NFlex等
Props 字典，包含组件的属性，仅限于基础属性，不能包含事件属性
    对于ref，可以直接在Props中定义路径数组，将自动设置计算属性
    对于v-model，可以直接在Props中定义路径数组，将自动设置事件
Slots 字典，可以包含子组件，将会设置()=>{}的事件
"""


class PropVarType(StrEnum):
    Value = "Value"  # 对应vue的 :xxx="xxx"
    VBind = "VBind"  # 对应vue的单向绑定
    VModel = "VModel"  # 对应vue的双向绑定


class PropVar(BaseModel):
    Type: PropVarType
    Data: Any
    pass

    """
    当PropVarType==Ref|VModel时，PropVar的Data应为路径数组
    例如：[THIS_NODE_DATA, "Payloads", "ById", "D_EXAM_TEXT", "Data"]
    """

    @field_validator("Data")
    @classmethod
    def check_data_when_ref_or_vmodel(cls, data, values: ValidationInfo):
        var_type = values.data.get("Type")

        if var_type in (PropVarType.VBind, PropVarType.VModel):
            if not isinstance(data, list):
                raise ValueError("Data must be a list when Type is Ref or VModel")

            if not data:
                raise ValueError("Data list cannot be empty")

        return data


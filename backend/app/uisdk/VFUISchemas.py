from typing import List, Dict, Any, Optional
from pydantic import BaseModel, field_validator, ValidationInfo
from enum import StrEnum

"""
vue数据结构定义
=============================
Type Value|VBind|VModel
Data 
    Value  对应vue的 :xxx="xxx"
    VBind  对应vue的单向绑定
    VModel  对应vue的双向绑定
"""

"""
vue组件定义
=============================
普通UI组件
Type 指向组件的类型，例如NInput，NFlex等
Props 字典，包含组件的属性，仅限于基础属性，不能包含事件属性
    对于v-bind，可以直接在Props中定义路径数组，将自动设置计算属性
    对于v-model，可以直接在Props中定义路径数组，将自动设置事件
Slots 字典，可以包含子组件，将会设置()=>{}的事件
=============================
Type 如果是@开头结尾，则表示是特殊组件
=============================
Type @Value@|@VBind@ 视作span
Data 对应组件的属性值，可以是字符串，数字，布尔值，也可以是路径数组
=============================
Type @FOR@ 视作 <template v-for="item in items"/>
Items vue数据结构
ItemLabel vue数据结构
IndexLabel vue数据结构
Template 组件|组件数组
"""
"""
v-if属性 使用IfCondition字段
=============================
Type 
    Value 直接使用数据作为判断条件
    VBind 直接使用数据作为判断条件
    Compare 
    Logical 

Type==Compare: 
    Left vue数据结构
    Operator 比较运算符，支持==，!=，>，<，>=，<=
    Right vue数据结构
Type==Logical: 
    Operator: 'AND' | 'OR'
    Conditions: Condition[] 可嵌套的条件数组
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
    当 PropVarType == VBind | VModel 时，PropVar的Data应为路径数组
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


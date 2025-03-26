from typing import Literal, Union, List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
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


# ================= 基础类型定义 =================
class PropVarType(StrEnum):
    Value = "@VALUE@"
    VBind = "@VBIND@"
    VModel = "@VMODEL@"
    FUNCTION = "@FUNCTION@"


class PropVarBase(BaseModel):
    Type: PropVarType


class ValueProp(PropVarBase):
    Type: Literal[PropVarType.Value] = PropVarType.Value
    Data: Any = Field(..., description="静态值")


class VBindProp(PropVarBase):
    Type: Literal[PropVarType.VBind] = PropVarType.VBind
    Data: List[Union[str, int]] = Field(
        ..., description="数据路径数组，如 ['path', 'to', 'data']", min_length=1
    )


class VModelProp(PropVarBase):
    Type: Literal[PropVarType.VModel] = PropVarType.VModel
    Data: List[Union[str, int]] = Field(
        ..., description="双向绑定路径数组", min_length=1
    )


class FunctionProp(PropVarBase):
    Type: Literal[PropVarType.FUNCTION]


PropVar = Union[ValueProp, VBindProp, VModelProp]
ReadOnlyPropVar = Union[ValueProp, VBindProp]


# ================= 条件系统 =================
class ConditionType(StrEnum):
    Compare = "@CONDITION_COMPARE@"
    Logical = "@CONDITION_LOGICAL@"
    Direct = "@CONDITION_DIRECT@"


class CompareCondition(BaseModel):
    Type: Literal[ConditionType.Compare]
    Left: ReadOnlyPropVar
    Operator: Literal["==", "!=", ">", "<", ">=", "<="]
    Right: ReadOnlyPropVar


class LogicalCondition(BaseModel):
    Type: Literal[ConditionType.Logical]
    Operator: Literal["AND", "OR"]
    Conditions: List["Condition"]


class DirectCondition(BaseModel):
    Type: Literal[ConditionType.Direct]
    Condition: ReadOnlyPropVar


Condition = Union[CompareCondition, LogicalCondition, DirectCondition]


# ================= 组件系统 =================
class ComponentType(StrEnum):
    VFOR = "@VFOR@"
    VALUE = "@VALUE@"
    VBIND = "@VBIND@"


class BaseComponent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    Type: str
    IfCondition: Optional[Condition] = None
    pass


class NormalComponent(BaseComponent):
    Type: str  # 任意字符串
    Props: Optional[Dict[str, PropVar]] = None
    Slots: Optional[Dict[str, Union["UnionComponent", List["UnionComponent"]]]] = None

    @model_validator(mode="after")
    def check_type_conflict(self):
        # 确保 Type 不与其他子类的固定值冲突
        forbidden_types = [ComponentType.VFOR, ComponentType.VBIND, ComponentType.VALUE]
        if self.Type in forbidden_types:
            raise ValueError(
                f"NormalComponent Type cannot be {self.Type}, "
                "use specific component types instead"
            )
        return self


class SpanComponent(BaseComponent):
    Type: Literal[ComponentType.VALUE, ComponentType.VBIND]
    Data: Union[Any, List[Union[str, int]]]  # 联合类型
    Props: Optional[Literal[None]] = Field(None, exclude=True)
    Slots: Optional[Literal[None]] = Field(None, exclude=True)

    @field_validator("Type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        allowed = [ComponentType.VBIND, ComponentType.VALUE]
        if v not in allowed:
            raise ValueError(f"Type must be one of {allowed}")
        return v


class ForLoopComponent(BaseComponent):
    Type: str = Field(default=ComponentType.VFOR, frozen=True)  # 固定值但允许校验
    Items: ReadOnlyPropVar
    ItemLabel: str
    IndexLabel: str
    Template: Union["UnionComponent", List["UnionComponent"]]
    Props: Optional[Literal[None]] = Field(None, exclude=True)
    Slots: Optional[Literal[None]] = Field(None, exclude=True)

    @field_validator("Type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v != ComponentType.VFOR:
            raise ValueError(f"Type must be {ComponentType.VFOR}")
        return v


UnionComponent = Union[NormalComponent, SpanComponent, ForLoopComponent]
for cls in [ForLoopComponent, SpanComponent, NormalComponent]:
    cls.model_rebuild()

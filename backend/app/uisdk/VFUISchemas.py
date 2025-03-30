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
    Function = "@FUNCTION@"


class PropVarBase(BaseModel):
    Type: PropVarType


# ================= 基础属性类型 =================
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


# ================= 函数类型增强 =================
class FunctionPropType(StrEnum):
    ADDITEM = "@ADDITEM@"
    REMOVEITEM = "@REMOVEITEM@"
    APPENDITEM = "@APPENDITEM@"
    ADDRESULT2OUT = "@ADDRESULT2OUT@"
    REMOVERESULT4OUT = "@REMOVERESULT4OUT@"
    OPENEDITOR = "@OPENEDITOR@"
    pass


class FuncArg_ADDITEM(BaseModel):
    DstPath: List[Union[str, int]] = Field(
        ..., description="目标路径数组", min_length=1
    )
    ItemValue: Any = Field(None, description="item的value数据")
    ItemKey: "ReadOnlyPropVar" = Field(..., description="item的key")
    pass


class FuncArg_REMOVEITEM(BaseModel):
    DstPath: List[Union[str, int]] = Field(
        ..., description="目标路径数组", min_length=1
    )
    ItemKey: "ReadOnlyPropVar" = Field(..., description="item的key")
    pass


class FuncArg_APPENDITEM(BaseModel):
    DstPath: List[Union[str, int]] = Field(
        ..., description="目标路径数组", min_length=1
    )
    ItemValue: Any = Field(None, description="item的value数据")
    pass


class FuncArg_ADDRESULT2OUT(BaseModel):
    HandleId: str = Field(..., description="输出句柄id")
    Result: Any = Field(..., description="结果数据")
    pass


class FuncArg_REMOVERESULT4OUT(BaseModel):
    ResultId: "ReadOnlyPropVar" = Field(..., description="结果id")
    pass


class FuncArg_OPENEDITOR(BaseModel):
    Language: str = Field(..., description="编辑器语言")
    DstPath: List[Union[str, int]] = Field(
        ..., description="目标路径数组", min_length=1
    )
    pass


# ================= 强化函数属性 =================
class _FunctionPropBase(PropVarBase):
    Type: Literal[PropVarType.Function] = PropVarType.Function
    Func: FunctionPropType


class ADDITEM_FuncProp(_FunctionPropBase):
    Func: Literal[FunctionPropType.ADDITEM] = FunctionPropType.ADDITEM
    Arg: FuncArg_ADDITEM


class REMOVEITEM_FuncProp(_FunctionPropBase):
    Func: Literal[FunctionPropType.REMOVEITEM] = FunctionPropType.REMOVEITEM
    Arg: FuncArg_REMOVEITEM


class APPENDITEM_FuncProp(_FunctionPropBase):
    Func: Literal[FunctionPropType.APPENDITEM] = FunctionPropType.APPENDITEM
    Arg: FuncArg_APPENDITEM


class ADDRESULT2OUT_FuncProp(_FunctionPropBase):
    Func: Literal[FunctionPropType.ADDRESULT2OUT] = FunctionPropType.ADDRESULT2OUT
    Arg: FuncArg_ADDRESULT2OUT


class REMOVERESULT4OUT_FuncProp(_FunctionPropBase):
    Func: Literal[FunctionPropType.REMOVERESULT4OUT] = FunctionPropType.REMOVERESULT4OUT
    Arg: FuncArg_REMOVERESULT4OUT


class OPENEDITOR_FuncProp(_FunctionPropBase):
    Func: Literal[FunctionPropType.OPENEDITOR] = FunctionPropType.OPENEDITOR
    Arg: FuncArg_OPENEDITOR


# ================= 最终联合类型 =================
FunctionProp = Union[
    ADDITEM_FuncProp,
    REMOVEITEM_FuncProp,
    APPENDITEM_FuncProp,
    ADDRESULT2OUT_FuncProp,
    REMOVERESULT4OUT_FuncProp,
    OPENEDITOR_FuncProp,
]

PropVar = Union[ValueProp, VBindProp, VModelProp, FunctionProp]
ReadOnlyPropVar = Union[ValueProp, VBindProp]


# ================= 条件系统 =================
class ConditionType(StrEnum):
    Compare = "@CONDITION_COMPARE@"
    Logical = "@CONDITION_LOGICAL@"
    Direct = "@CONDITION_DIRECT@"


class CompareCondition(BaseModel):
    Type: Literal[ConditionType.Compare] = ConditionType.Compare
    Left: ReadOnlyPropVar
    Operator: Literal["==", "!=", ">", "<", ">=", "<="]
    Right: ReadOnlyPropVar


class LogicalCondition(BaseModel):
    Type: Literal[ConditionType.Logical] = ConditionType.Logical
    Operator: Literal["AND", "OR"]
    Conditions: List["Condition"]


class DirectCondition(BaseModel):
    Type: Literal[ConditionType.Direct] = ConditionType.Direct
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

    @field_validator("Props", mode="before")
    @classmethod
    def convert_props(
        cls, props: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, PropVar]]:
        """在验证前自动将普通 dict 转换为 PropVar 格式"""
        if props is None:
            return None
        result_props = {}
        for key, value in props.items():
            if value is None:
                continue
            if not isinstance(value, PropVar):
                result_props[key] = ValueProp(Data=value)
            else:
                result_props[key] = value
        return result_props


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

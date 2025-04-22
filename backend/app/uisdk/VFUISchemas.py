from typing import Literal, Union, List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from enum import StrEnum
from app.schemas.VFNodeInterface import (
    VFNodeConnectionType,
    VFNodeHandleData,
    VFNodeContentData,
    FromInnerPath,
)
from app.schemas.VFNodeClass import InsertPos


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

    def __init__(self, data=None, **kwargs):
        if not "Data" in kwargs:
            kwargs["Data"] = data
        super().__init__(**kwargs)


class VBindProp(PropVarBase):
    Type: Literal[PropVarType.VBind] = PropVarType.VBind
    Data: List[Union[str, int, ValueProp, "VBindProp"]] = Field(
        ..., description="数据路径数组", min_length=1
    )
    Replace: Optional[str] = Field(None, description="替换模板")

    def __init__(self, data=None, replace=None, **kwargs):
        """
        初始化 VBindProp 对象
        如果传入的第一个参数是列表，则将其作为 Data 字段的值
        否则使用标准的关键字参数初始化
        """
        if data is not None and isinstance(data, list) and not "Data" in kwargs:
            kwargs["Data"] = data
        if replace is not None:
            kwargs["Replace"] = replace
        super().__init__(**kwargs)

    @model_validator(mode="after")
    def check_data_type(self):
        """
        递归将Data中的str, int转换为ValueProp
        需要递归解包VBindProp的内容
        """
        for i, item in enumerate(self.Data):
            if isinstance(item, (str, int)):
                self.Data[i] = ValueProp(Data=item)
            elif isinstance(item, VBindProp):
                item.check_data_type()
        return self


class VModelProp(PropVarBase):
    Type: Literal[PropVarType.VModel] = PropVarType.VModel
    Data: List[Union[str, int, ValueProp, VBindProp]] = Field(
        ..., description="双向绑定路径数组", min_length=1
    )

    def __init__(self, data=None, **kwargs):
        if data is not None and isinstance(data, list) and not "Data" in kwargs:
            kwargs["Data"] = data
        super().__init__(**kwargs)

    @model_validator(mode="after")
    def check_data_type(self):
        for i, item in enumerate(self.Data):
            if isinstance(item, (str, int)):
                self.Data[i] = ValueProp(Data=item)
            elif isinstance(item, VBindProp):
                item.check_data_type()
        return self


# ================= 函数类型增强 =================
class FunctionPropType(StrEnum):
    SETCONTEXT = "@SETCONTEXT@"
    ADDITEM = "@ADDITEM@"
    REMOVEITEM = "@REMOVEITEM@"
    APPENDITEM = "@APPENDITEM@"
    ADDRESULT = "@ADDRESULT@"
    REMOVERESULT = "@REMOVERESULT@"
    ADDRESULT2OUT = "@ADDRESULT2OUT@"
    REMOVERESULT4OUT = "@REMOVERESULT4OUT@"
    ADDHANDLE = "@ADDHANDLE@"
    REMOVEHANDLE = "@REMOVEHANDLE@"
    ADDHANDLEDATA = "@ADDHANDLEDATA@"
    REMOVEHANDLEDATA = "@REMOVEHANDLEDATA@"
    UPDATENODEINTERNAL = "@UPDATENODEINTERNAL@"
    OPENEDITOR = "@OPENEDITOR@"
    pass


class FuncArg_SETCONTEXT(BaseModel):
    Key: "ReadOnlyPropVar" = Field(..., description="上下文键名")
    Value: "ReadOnlyPropVar" = Field(..., description="上下文值")
    pass


class FuncArg_ADDITEM(BaseModel):
    DstPath: VBindProp = Field(..., description="目标路径数组")
    ItemValue: Any = Field(..., description="item的value数据")
    ItemKey: "ReadOnlyPropVar" = Field(..., description="item的key")
    pass


class FuncArg_REMOVEITEM(BaseModel):
    DstPath: VBindProp = Field(..., description="目标路径数组")
    ItemKey: "ReadOnlyPropVar" = Field(..., description="item的key")
    pass


class FuncArg_APPENDITEM(BaseModel):
    DstPath: VBindProp = Field(..., description="目标路径数组")
    ItemValue: Any = Field(..., description="item的value数据")
    pass


class FuncArg_ADDRESULT(BaseModel):
    Result: VFNodeContentData = Field(..., description="结果数据")
    ResultId: Optional["ReadOnlyPropVar"] = Field(None, description="结果id")
    Position: Optional[InsertPos] = Field(InsertPos.End, description="插入位置")
    pass


class FuncArg_REMOVERESULT(BaseModel):
    ResultId: "ReadOnlyPropVar" = Field(..., description="结果id")
    pass


class FuncArg_ADDRESULT2OUT(BaseModel):
    HandleId: "ReadOnlyPropVar" = Field(..., description="输出句柄id")
    Result: VFNodeContentData = Field(..., description="结果数据")
    Position: Optional[InsertPos] = Field(InsertPos.End, description="插入位置")
    ResultId: Optional["ReadOnlyPropVar"] = Field(None, description="结果id")
    DataId: Optional["ReadOnlyPropVar"] = Field(None, description="连接数据id")
    pass


class FuncArg_REMOVERESULT4OUT(BaseModel):
    ResultId: "ReadOnlyPropVar" = Field(..., description="结果id")
    pass


class FuncArg_OPENEDITOR(BaseModel):
    Language: str = Field(..., description="编辑器语言")
    DstPath: VBindProp = Field(..., description="目标路径数组")
    pass


class FuncArg_ADDHANDLE(BaseModel):
    HandleType: VFNodeConnectionType = Field(..., description="句柄类型")
    HandleId: Optional["ReadOnlyPropVar"] = Field(..., description="句柄id")
    Position: Optional[InsertPos] = Field(InsertPos.End, description="插入位置")
    HandleLabel: Optional["ReadOnlyPropVar"] = Field(None, description="句柄标签")
    pass


class FuncArg_REMOVEHANDLE(BaseModel):
    HandleType: VFNodeConnectionType = Field(..., description="句柄类型")
    HandleId: Optional["ReadOnlyPropVar"] = Field(..., description="句柄id")
    pass


class FuncArg_ADDHANDLEDATA(BaseModel):
    HandleType: VFNodeConnectionType = Field(..., description="句柄类型")
    HandleId: Optional["ReadOnlyPropVar"] = Field(..., description="句柄id")
    Data: VFNodeHandleData = Field(..., description="数据")
    DataId: Optional["ReadOnlyPropVar"] = Field(None, description="连接数据id")
    pass


class FuncArg_REMOVEHANDLEDATA(BaseModel):
    HandleType: VFNodeConnectionType = Field(..., description="句柄类型")
    HandleId: Optional["ReadOnlyPropVar"] = Field(..., description="句柄id")
    DataId: Optional["ReadOnlyPropVar"] = Field(..., description="连接数据id")
    pass


# ================= 强化函数属性 =================


class _FuncPropBase(BaseModel):
    Func: FunctionPropType
    Arg: Any


class SETCONTEXT_FuncProp(_FuncPropBase):
    Func: Literal[FunctionPropType.SETCONTEXT] = FunctionPropType.SETCONTEXT
    Arg: FuncArg_SETCONTEXT


class ADDITEM_FuncProp(_FuncPropBase):
    Func: Literal[FunctionPropType.ADDITEM] = FunctionPropType.ADDITEM
    Arg: FuncArg_ADDITEM


class REMOVEITEM_FuncProp(_FuncPropBase):
    Func: Literal[FunctionPropType.REMOVEITEM] = FunctionPropType.REMOVEITEM
    Arg: FuncArg_REMOVEITEM


class APPENDITEM_FuncProp(_FuncPropBase):
    Func: Literal[FunctionPropType.APPENDITEM] = FunctionPropType.APPENDITEM
    Arg: FuncArg_APPENDITEM


class ADDRESULT_FuncProp(_FuncPropBase):
    Func: Literal[FunctionPropType.ADDRESULT] = FunctionPropType.ADDRESULT
    Arg: FuncArg_ADDRESULT


class REMOVERESULT_FuncProp(_FuncPropBase):
    Func: Literal[FunctionPropType.REMOVERESULT] = FunctionPropType.REMOVERESULT
    Arg: FuncArg_REMOVERESULT


class ADDRESULT2OUT_FuncProp(_FuncPropBase):
    Func: Literal[FunctionPropType.ADDRESULT2OUT] = FunctionPropType.ADDRESULT2OUT
    Arg: FuncArg_ADDRESULT2OUT


class REMOVERESULT4OUT_FuncProp(_FuncPropBase):
    Func: Literal[FunctionPropType.REMOVERESULT4OUT] = FunctionPropType.REMOVERESULT4OUT
    Arg: FuncArg_REMOVERESULT4OUT


class ADDHANDLE_FuncProp(_FuncPropBase):
    Func: Literal[FunctionPropType.ADDHANDLE] = FunctionPropType.ADDHANDLE
    Arg: FuncArg_ADDHANDLE


class REMOVEHANDLE_FuncProp(_FuncPropBase):
    Func: Literal[FunctionPropType.REMOVEHANDLE] = FunctionPropType.REMOVEHANDLE
    Arg: FuncArg_REMOVEHANDLE


class ADDHANDLEDATA_FuncProp(_FuncPropBase):
    Func: Literal[FunctionPropType.ADDHANDLEDATA] = FunctionPropType.ADDHANDLEDATA
    Arg: FuncArg_ADDHANDLEDATA


class REMOVEHANDLEDATA_FuncProp(_FuncPropBase):
    Func: Literal[FunctionPropType.REMOVEHANDLEDATA] = FunctionPropType.REMOVEHANDLEDATA
    Arg: FuncArg_REMOVEHANDLEDATA


class UPDATENODEINTERNAL_FuncProp(_FuncPropBase):
    Func: Literal[FunctionPropType.UPDATENODEINTERNAL] = (
        FunctionPropType.UPDATENODEINTERNAL
    )
    Arg: Any = None


class OPENEDITOR_FuncProp(_FuncPropBase):
    Func: Literal[FunctionPropType.OPENEDITOR] = FunctionPropType.OPENEDITOR
    Arg: FuncArg_OPENEDITOR


SingleFunctionProp = Union[
    SETCONTEXT_FuncProp,
    ADDITEM_FuncProp,
    REMOVEITEM_FuncProp,
    APPENDITEM_FuncProp,
    ADDRESULT_FuncProp,
    REMOVERESULT_FuncProp,
    ADDRESULT2OUT_FuncProp,
    REMOVERESULT4OUT_FuncProp,
    ADDHANDLE_FuncProp,
    REMOVEHANDLE_FuncProp,
    ADDHANDLEDATA_FuncProp,
    REMOVEHANDLEDATA_FuncProp,
    UPDATENODEINTERNAL_FuncProp,
    OPENEDITOR_FuncProp,
]


class FunctionProp(PropVarBase):
    Type: Literal[PropVarType.Function] = PropVarType.Function
    Funcs: List[SingleFunctionProp]


# ================= 最终联合类型 =================
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
    VSPAN = "@VSPAN@"


class BaseComponent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    Type: str
    IfCondition: Optional[Condition] = None


class NormalComponent(BaseComponent):
    Type: str  # 任意字符串
    Props: Optional[Dict[str, PropVar]] = None
    Slots: Optional[Dict[str, Union["UnionComponent", List["UnionComponent"]]]] = None

    @model_validator(mode="after")
    def check_type_conflict(self):
        # 确保 Type 不与其他子类的固定值冲突
        forbidden_types = [ComponentType.VFOR, ComponentType.VSPAN]
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
                result_props[key] = ValueProp(value)
            else:
                result_props[key] = value
        return result_props


class SpanComponent(BaseComponent):
    Type: str = Field(default=ComponentType.VSPAN, frozen=True)  # 固定值但允许校验
    Data: "ReadOnlyPropVar"
    Replace: Optional[str] = Field(None, description="替换模板")
    Props: Optional[Literal[None]] = Field(None, exclude=True)
    Slots: Optional[Literal[None]] = Field(None, exclude=True)

    @field_validator("Type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v != ComponentType.VSPAN:
            raise ValueError(f"Type must be {ComponentType.VSPAN}")
        return v

    def __init__(self, data=None, replace=None, **kwargs):
        if data is not None and isinstance(data, ReadOnlyPropVar):
            kwargs["Data"] = data
        if replace is not None:
            kwargs["Replace"] = replace
        super().__init__(**kwargs)


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
for cls in [
    ForLoopComponent,
    SpanComponent,
    NormalComponent,
    ValueProp,
    VBindProp,
    VModelProp,
    FunctionProp,
]:
    cls.model_rebuild()


class SelectOptions(BaseModel):
    label: str
    value: str
    pass


class VarType(StrEnum):
    Ref = "Ref"
    String = "String"
    Integer = "Integer"
    Number = "Number"
    Boolean = "Boolean"
    File = "File"
    Any = "Any"
    pass

class RefVarItem(BaseModel):
    Nid: str
    Path: FromInnerPath
    pass


class RefNodeHandleItem(BaseModel):
    Node: str
    HandleType: VFNodeConnectionType
    Handle: str
    pass

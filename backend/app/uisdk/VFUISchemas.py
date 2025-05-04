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
    OperateFunc = "@OPERATEFUNC@"
    ReturnFunc = "@RETURNFUNC@"
    AReturnFunc = "@ARETURNFUNC@"


class PropVarBase(BaseModel):
    FA_Type__: PropVarType


# ================= 基础属性类型 =================
class ValueProp(PropVarBase):
    FA_Type__: Literal[PropVarType.Value] = PropVarType.Value
    FA_Data__: Any = Field(..., description="静态值")

    def __init__(self, data: Any, **kwargs):
        if not "FA_Data__" in kwargs:
            kwargs["FA_Data__"] = data
        super().__init__(**kwargs)


class VBindProp(PropVarBase):
    FA_Type__: Literal[PropVarType.VBind] = PropVarType.VBind
    FA_Data__: List[Union[str, int, ValueProp, "VBindProp"]] = Field(
        ..., description="数据路径数组", min_length=1
    )
    FA_Replace__: Optional[str] = Field(None, description="替换模板")

    def __init__(self, data: list, replace: Optional[str] = None, **kwargs):
        """
        初始化 VBindProp 对象
        如果传入的第一个参数是列表，则将其作为 Data 字段的值
        否则使用标准的关键字参数初始化
        """
        if isinstance(data, list) and not "FA_Data__" in kwargs:
            kwargs["FA_Data__"] = data
        if replace is not None:
            kwargs["FA_Replace__"] = replace
        super().__init__(**kwargs)

    @model_validator(mode="after")
    def check_data_type(self):
        """
        递归将Data中的str, int转换为ValueProp
        需要递归解包VBindProp的内容
        """
        for i, item in enumerate(self.FA_Data__):
            if isinstance(item, (str, int)):
                self.FA_Data__[i] = ValueProp(item)
            elif isinstance(item, VBindProp):
                item.check_data_type()
        return self


class VModelProp(PropVarBase):
    FA_Type__: Literal[PropVarType.VModel] = PropVarType.VModel
    FA_Data__: List[Union[str, int, ValueProp, VBindProp]] = Field(
        ..., description="双向绑定路径数组", min_length=1
    )

    def __init__(self, data: list, **kwargs):
        if isinstance(data, list) and not "FA_Data__" in kwargs:
            kwargs["FA_Data__"] = data
        super().__init__(**kwargs)

    @model_validator(mode="after")
    def check_data_type(self):
        for i, item in enumerate(self.FA_Data__):
            if isinstance(item, (str, int)):
                self.FA_Data__[i] = ValueProp(item)
            elif isinstance(item, VBindProp):
                item.check_data_type()
        return self


# ================= 函数类型增强 =================
class FunctionPropType(StrEnum):
    # Operate =======================
    SETCONTEXT = "@SETCONTEXT@"
    ADDITEM = "@ADDITEM@"
    REMOVEITEM = "@REMOVEITEM@"
    APPENDITEM = "@APPENDITEM@"
    ADDPAYLOAD = "@ADDPAYLOAD@"
    REMOVEPAYLOAD = "@REMOVEPAYLOAD@"
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
    DELETEIMAGE = "@DELETEIMAGE@"
    # Return =======================
    UPLOADIMAGE = "@UPLOADIMAGE@"
    GENERATEUUID = "@GENERATEUUID@"
    FORMATSTRING = "@FORMATSTRING@"
    BACKENDURL = "@BACKENDURL@"
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
    Position: Optional[InsertPos] = Field(InsertPos.End, description="插入位置")
    pass


class FuncArg_ADDPAYLOAD(BaseModel):
    Payload: VFNodeContentData = Field(..., description="载荷数据")
    PayloadId: Optional["ReadOnlyPropVar"] = Field(None, description="载荷id")
    Position: Optional[InsertPos] = Field(InsertPos.End, description="插入位置")
    pass


class FuncArg_REMOVEPAYLOAD(BaseModel):
    PayloadId: "ReadOnlyPropVar" = Field(..., description="载荷id")
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


class FuncArg_FORMATSTRING(BaseModel):
    FString: str = Field(..., description="格式化字符串")
    Args: Dict[str, "ReadOnlyPropVar"] = Field(..., description="格式化参数")
    pass


class FuncArg_DELETEIMAGE(BaseModel):
    Filename: "ReadOnlyPropVar" = Field(..., description="文件名")
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


class ADDPAYLOAD_FuncProp(_FuncPropBase):
    Func: Literal[FunctionPropType.ADDPAYLOAD] = FunctionPropType.ADDPAYLOAD
    Arg: FuncArg_ADDPAYLOAD


class REMOVEPAYLOAD_FuncProp(_FuncPropBase):
    Func: Literal[FunctionPropType.REMOVEPAYLOAD] = FunctionPropType.REMOVEPAYLOAD
    Arg: FuncArg_REMOVEPAYLOAD


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


class UPLOADIMAGE_FuncProp(_FuncPropBase):
    Func: Literal[FunctionPropType.UPLOADIMAGE] = FunctionPropType.UPLOADIMAGE
    Arg: Any = None


class GENERATEUUID_FuncProp(_FuncPropBase):
    Func: Literal[FunctionPropType.GENERATEUUID] = FunctionPropType.GENERATEUUID
    Arg: Any = None


class FORMATSTRING_FuncProp(_FuncPropBase):
    Func: Literal[FunctionPropType.FORMATSTRING] = FunctionPropType.FORMATSTRING
    Arg: FuncArg_FORMATSTRING


class DELETEIMAGE_FuncProp(_FuncPropBase):
    Func: Literal[FunctionPropType.DELETEIMAGE] = FunctionPropType.DELETEIMAGE
    Arg: FuncArg_DELETEIMAGE

class BACKENDURL_FuncProp(_FuncPropBase):
    Func: Literal[FunctionPropType.BACKENDURL] = FunctionPropType.BACKENDURL
    Arg: Any = None

Operate_FuncProps = Union[
    SETCONTEXT_FuncProp,
    ADDITEM_FuncProp,
    REMOVEITEM_FuncProp,
    APPENDITEM_FuncProp,
    ADDPAYLOAD_FuncProp,
    REMOVEPAYLOAD_FuncProp,
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
    DELETEIMAGE_FuncProp,
]
Return_FuncProps = Union[
    GENERATEUUID_FuncProp,
    FORMATSTRING_FuncProp,
    BACKENDURL_FuncProp,
]
AsyncReturn_FuncProps = Union[UPLOADIMAGE_FuncProp,]


class OperateFunctionProp(PropVarBase):
    FA_Type__: Literal[PropVarType.OperateFunc] = PropVarType.OperateFunc
    FA_Funcs__: List[Operate_FuncProps]

    def __init__(self, funcs: List[Operate_FuncProps], **kwargs):
        if not "FA_Funcs__" in kwargs:
            kwargs["FA_Funcs__"] = funcs
        super().__init__(**kwargs)


class ReturnFunctionProp(PropVarBase):
    FA_Type__: Literal[PropVarType.ReturnFunc] = PropVarType.ReturnFunc
    FA_Func__: Return_FuncProps

    def __init__(self, func: Return_FuncProps, **kwargs):
        if not "FA_Func__" in kwargs:
            kwargs["FA_Func__"] = func
        super().__init__(**kwargs)


class AsyncReturnFunctionProp(PropVarBase):
    FA_Type__: Literal[PropVarType.AReturnFunc] = PropVarType.AReturnFunc
    FA_Func__: AsyncReturn_FuncProps

    def __init__(self, func: AsyncReturn_FuncProps, **kwargs):
        if not "FA_Func__" in kwargs:
            kwargs["FA_Func__"] = func
        super().__init__(**kwargs)


# ================= 最终联合类型 =================
PropVar = Union[
    ValueProp,
    VBindProp,
    VModelProp,
    OperateFunctionProp,
    ReturnFunctionProp,
    AsyncReturnFunctionProp,
]
ReadOnlyPropVar = Union[
    ValueProp,
    VBindProp,
    ReturnFunctionProp,
    AsyncReturnFunctionProp,
]


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
    OperateFunctionProp,
    ReturnFunctionProp,
]:
    cls.model_rebuild()


class SelectOptions(BaseModel):
    label: str
    value: str
    pass

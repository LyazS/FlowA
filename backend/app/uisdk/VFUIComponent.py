from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, field_validator
from app.uisdk.VFUISchemas import PropVar, PropVarType


class BaseComponent(BaseModel):
    """
    Type 指向组件的类型，例如NInput，NFlex等
    Props 字典，包含组件的属性，仅限于基础属性，不能包含事件属性
        对于ref，可以直接在Props中定义路径数组，将自动设置计算属性
        对于v-model，可以直接在Props中定义路径数组，将自动设置事件
    Slots 字典，可以包含子组件，将会设置()=>{}的事件
    """

    Type: str
    Props: Dict
    Slots: Optional[Dict[str, Union["BaseComponent", List["BaseComponent"]]]]
    IfCondition: Any = None
    pass

    @field_validator("Props")
    @classmethod
    def convert_props(cls, props: Dict):
        return {
            key: (
                PropVar(Type=PropVarType.Value, Data=value)
                if not isinstance(value, PropVar)
                else value
            )
            for key, value in props.items()
        }

    @field_validator("Slots")
    @classmethod
    def convert_Slots(cls, Slots: Optional[Dict]):
        if Slots is None:
            return {}
        else:
            return Slots

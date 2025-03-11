from typing import List, Dict
from pydantic import BaseModel

"""
Type 指向组件的类型，例如NInput，NFlex等
Props 字典，包含组件的属性，仅限于基础属性，不能包含事件属性
    对于v-model，可以直接在Props中定义，将自动设置事件
Slots 字典，可以包含子组件，将会设置()=>{}的事件
"""

class BaseComponent(BaseModel):
    Type: str
    Props: Dict
    Slots: Dict
    pass


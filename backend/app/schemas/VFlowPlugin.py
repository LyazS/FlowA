import unicodedata
from typing import List, Optional, Any, Union
from pydantic import BaseModel, field_validator, ValidationInfo
from app.uisdk.VFUIComponent import BaseComponent
from app.schemas.VFNodeClass import VFNode


class VFPluginSetting(BaseModel):
    Execute: str


class VFPlugin(BaseModel):
    Type: str
    Name: str
    Label: str
    Description: str
    Execute: str
    Setting: Optional[VFPluginSetting]
    CreateInfo: Optional[VFNode] = None
    pass


class VFUIPlugin(BaseModel):
    Type: str
    Name: str
    Component: Union[str, BaseComponent]


class VFProvider(BaseModel):
    Provider: str
    Label: str
    Version: str
    Description: str
    Author: str
    Icon: Optional[str]
    ProviderSetting: Optional[VFPluginSetting]
    Plugins: List[VFPlugin]
    UIPlugins: List[VFUIPlugin]

    @field_validator("Provider")
    @classmethod
    def validate_provider_name(cls, data: str, values: ValidationInfo):
        """验证Provider名称格式"""
        allowed_symbols = {"_", "-"}

        for char in data:
            # 允许：空格、字母、数字、文字符及白名单符号
            if char.isspace() or char in allowed_symbols:
                continue

            # 禁止：所有Unicode标点符号（P开头的类别）
            if unicodedata.category(char).startswith("P"):
                raise ValueError(
                    f"非法字符 '{char}'，Provider名称仅允许使用："
                    "字母/数字/文字/空格/下划线(_)/连字符(-)"
                )

        return data


class VFProviders(BaseModel):
    Providers: List[VFProvider]

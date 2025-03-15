from typing import List, Optional, Any, Union
from pydantic import BaseModel
from app.schemas.VFUIComponent import BaseComponent


class VFPluginSetting(BaseModel):
    Execute: str


class VFPlugin(BaseModel):
    Type: str
    Name: str
    Description: str
    Execute: str
    Setting: VFPluginSetting
    pass


class VFUIPlugin(BaseModel):
    Type: str
    Name: str
    Component: Union[str, BaseComponent]


class VFProvider(BaseModel):
    Provider: str
    Version: str
    Description: str
    Author: str
    Icon: Optional[str]
    ProviderSetting: VFPluginSetting
    Plugins: List[VFPlugin]
    UIPlugins: List[VFUIPlugin]


class VFProviders(BaseModel):
    Providers: List[VFProvider]

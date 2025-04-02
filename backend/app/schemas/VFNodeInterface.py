from enum import Enum, StrEnum, IntEnum
from typing import Dict, List, Optional, Union, Literal, Any
from pydantic import BaseModel, Field, model_validator
from app.utils.vueRef import RefType


class VFNodeConnectionDataType(str, Enum):
    FromOuter = "FromOuter"
    FromAttached = "FromAttached"
    FromParent = "FromParent"
    FromInner = "FromInner"


class VFNodeConnectionType(StrEnum):
    Self = "Self"
    Attach = "Attach"
    Inputs = "Inputs"
    Outputs = "Outputs"
    CallbackUsers = "CallbackUsers"
    CallbackFuncs = "CallbackFuncs"


class VFNodeFlag(IntEnum):
    IsNone = 0x00
    IsNested = 0x01
    IsAttached = 0x02
    IsTask = 0x04
    IsPassive = 0x08


class VFNodeAttachingType(StrEnum):
    Input = "Input"
    Output = "Output"
    CallbackFunc = "CallbackFunc"
    CallbackUser = "CallbackUser"


class VFNodeAttachingPosType(StrEnum):
    Top = "Top"
    Bottom = "Bottom"
    Left = "Left"
    Right = "Right"
    Center = "Center"


CodeEditorLanguage = Literal["python", "json", "django", "text"]


class VFNodeContentDataConfig(BaseModel):
    Language: Optional[CodeEditorLanguage] = None
    Ref: Optional[str] = None


class VFNodeContentData(BaseModel):
    Label: str
    Type: str
    # Key: str
    Data: RefType
    Config: Optional[VFNodeContentDataConfig] = None
    Hid: Optional[str] = None
    Did: Optional[str] = None
    UiType: Optional[str] = None


class VFNodeContents(BaseModel):
    ById: Dict[str, VFNodeContentData]
    Order: List[str]


class VFNodeHandleDataANode(BaseModel):
    ConnectionType: VFNodeConnectionType
    HandleId: str
    pass


class VFNodeHandleData(BaseModel):
    Type: VFNodeConnectionDataType
    HandleId: Optional[str] = None
    ANode: Optional[Dict[str, VFNodeHandleDataANode]] = None
    Path: Optional[List[Union[str, int]]] = None
    UseIds: Optional[List[str]] = None

    @model_validator(mode="after")
    def check_consistency(self):
        if self.Type == VFNodeConnectionDataType.FromInner and not self.Path:
            raise ValueError("FromInner连接类型必须包含Path字段")
        if self.Type == VFNodeConnectionDataType.FromAttached and not self.ANode:
            raise ValueError("FromAttached连接类型必须包含ANode字段")
        if self.Type == VFNodeConnectionDataType.FromOuter and not self.HandleId:
            raise ValueError("FromOuter连接类型必须包含HandleId字段")
        if self.Type == VFNodeConnectionDataType.FromParent and not self.HandleId:
            raise ValueError("FromParent连接类型必须包含HandleId字段")
        return self


class VFNodeHandle(BaseModel):
    Label: str
    Data: Dict[str, VFNodeHandleData]


class VFNodeConnections(BaseModel):
    Self: Dict[str, VFNodeHandle] = {}
    Attach: Dict[str, VFNodeHandle] = {}
    Inputs: Dict[str, VFNodeHandle] = {}
    Outputs: Dict[str, VFNodeHandle] = {}
    CallbackUsers: Dict[str, VFNodeHandle] = {}
    CallbackFuncs: Dict[str, VFNodeHandle] = {}


class VFNodeAttachingPos(BaseModel):
    XType: VFNodeAttachingPosType
    XOffset: int
    YType: VFNodeAttachingPosType
    YOffset: int
    pass


class VFNodeAttaching(BaseModel):
    Type: VFNodeAttachingType
    Pos: VFNodeAttachingPos
    Label: str


class VFNodeAttachedNode(BaseModel):
    Nid: Optional[str] = None
    NType: str
    # Type: VFNodeAttachingType
    # Pos: VFNodeAttachingPos
    # Label: str


class VFNodePadding(BaseModel):
    Top: int
    Bottom: int
    Left: int
    Right: int
    Gap: int


class VFNodeSize(BaseModel):
    Width: int
    Height: int


class VFNodeNesting(BaseModel):
    Tag: Optional[str] = None
    Pad: VFNodePadding
    APad: VFNodePadding
    ANodes: Dict[str, VFNodeAttachedNode]
    pass


class VFNodeState(BaseModel):
    Status: str
    Copy: Dict[str, Any] = {}
    CopyCount: Dict[str, int] = {"Running": 0, "Success": 0, "Error": 0}
    Errors: List[str] = []


class VFNodeConfig(BaseModel):
    OutputsUiType: str


class VFNodeData(BaseModel):
    NType: str
    VType: str
    Flag: int
    Label: str
    PlaceholderLabel: str
    Size: VFNodeSize
    Connections: VFNodeConnections
    Payloads: VFNodeContents
    Results: VFNodeContents
    State: VFNodeState
    Config: VFNodeConfig
    MinSize: Optional[VFNodeSize] = None  # 所有节点都可能有的字段
    Attaching: Optional[VFNodeAttaching] = None  # 所有节点都可能有的字段
    Nesting: Optional[VFNodeNesting] = None  # 所有节点都可能有的字段
    pass

    # 自定义校验器（确保Flag和字段一致性）
    @model_validator(mode="after")
    def check_flag_consistency(self):
        if self.Flag & VFNodeFlag.IsAttached and not self.Attaching:
            raise ValueError("Attached节点必须包含Attaching字段")
        if self.Flag & VFNodeFlag.IsNested and (not self.MinSize or not self.Nesting):
            raise ValueError("Nested节点必须包含MinSize和Nesting字段")
        return self

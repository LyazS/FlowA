from enum import Enum, StrEnum,IntEnum
from typing import Dict, List, Optional, Union, Literal, Any
from pydantic import BaseModel


class VFNodeConnectionDataType(str, Enum):
    FromOuter = "FromOuter"
    FromAttached = "FromAttached"
    FromParent = "FromParent"
    FromInner = "FromInner"


class VFNodeConnectionDataAttachedType(str, Enum):
    attached_node_input = "attached_node_input"
    attached_node_callbackUser = "attached_node_callbackUser"
    attached_node_output = "attached_node_output"
    attached_node_next = "attached_node_next"
    attached_node_callbackFunc = "attached_node_callbackFunc"
    attached_node_break = "attached_node_break"


class VFNodeConnectionType(StrEnum):
    Self = "Self"
    Attach = "Attach"
    Inputs = "Inputs"
    Outputs = "Outputs"
    CallbackUsers = "CallbackUsers"
    CallbackFuncs = "CallbackFuncs"


class VFNodeFlag(IntEnum):
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
    Key: str
    Data: Any
    Config: Optional[VFNodeContentDataConfig] = None
    Hid: Optional[str] = None
    Did: Optional[str] = None
    UiType: Optional[str] = None


class VFNodeContents(BaseModel):
    ById: Dict[str, VFNodeContentData]
    Order: List[str]


class VFNodeHandleData(BaseModel):
    Type: VFNodeConnectionDataType
    InputKey: Optional[str] = None
    AType: Optional[VFNodeConnectionDataAttachedType] = None
    Path: Optional[List[Union[str, int]]] = None
    UseIds: Optional[List[str]] = None


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
    Type: VFNodeAttachingType
    Pos: VFNodeAttachingPos
    Label: str


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
    ANodes: Dict[VFNodeConnectionDataAttachedType, VFNodeAttachedNode] = {}


class VFNodeState(BaseModel):
    Status: str
    Copy: Dict[str, Any] = {}
    CopyCount: Dict[str, int] = {"Running": 0, "Success": 0, "Error": 0}
    Errors: List[str] = []


class VFNodeConfig(BaseModel):
    OutputsUiType: str


class BaseVFNodeData(BaseModel):
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


class AttachedVFNodeData(BaseVFNodeData):
    Attaching: VFNodeAttaching


class NestedVFNodeData(BaseVFNodeData):
    MinSize: VFNodeSize
    Nesting: VFNodeNesting


VFNodeData = Union[BaseVFNodeData, AttachedVFNodeData, NestedVFNodeData]


def is_attached_node(node: VFNodeData) -> bool:
    return bool(node.Flag & VFNodeFlag.IsAttached)


def is_nested_node(node: VFNodeData) -> bool:
    return bool(node.Flag & VFNodeFlag.IsNested)

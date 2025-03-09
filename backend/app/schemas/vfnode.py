import asyncio
import uuid
from typing import List, Any, Dict, Optional, Union
from enum import Enum, Flag
from pydantic import BaseModel
import json
from .vfnode_contentdata import VFNodeContentDataType
from app.utils.vueRef import RefType


class VFNodeContentDataConfig(BaseModel):
    ref: Optional[str] = None
    language: Optional[str] = None

class VFNodeContentData(BaseModel):
    label: str
    type: VFNodeContentDataType
    key: str
    data: RefType
    config: Optional[VFNodeContentDataConfig] = None
    hid: Optional[str] = None
    oid: Optional[str] = None
    pass


class VFNodeContents(BaseModel):
    byId: Dict[str, VFNodeContentData]
    order: List[str]
    pass


class VFNodeConnectionDataType(Enum):
    FromOuter = "FromOuter"
    FromAttached = "FromAttached"
    FromParent = "FromParent"
    FromInner = "FromInner"
    pass


class VFNodeConnectionDataAttachedType(Enum):
    attached_node_input = "attached_node_input"
    attached_node_callbackUser = "attached_node_callbackUser"
    attached_node_output = "attached_node_output"
    attached_node_next = "attached_node_next"
    attached_node_callbackFunc = "attached_node_callbackFunc"
    attached_node_break = "attached_node_break"
    pass


class VFNodeConnectionData(BaseModel):
    type: VFNodeConnectionDataType
    inputKey: Optional[str] = None
    atype: Optional[VFNodeConnectionDataAttachedType] = None
    path: Optional[List[str]] = None
    useid: Optional[List[str]] = None
    pass


class VFNodeConnectionType(Enum):
    self = "self"
    attach = "attach"
    next = "next"
    breakIter = "break"
    inputs = "inputs"
    outputs = "outputs"
    callbackUsers = "callbackUsers"
    callbackFuncs = "callbackFuncs"
    pass


class VFNodeConnection(BaseModel):
    label: str
    data: Dict[str, VFNodeConnectionData]
    pass


class VFNodeConnections(BaseModel):
    self: Optional[Dict[str, VFNodeConnection]] = None
    attach: Optional[Dict[str, VFNodeConnection]] = None
    next: Optional[Dict[str, VFNodeConnection]] = None
    inputs: Optional[Dict[str, VFNodeConnection]] = None
    outputs: Optional[Dict[str, VFNodeConnection]] = None
    callbackUsers: Optional[Dict[str, VFNodeConnection]] = None
    callbackFuncs: Optional[Dict[str, VFNodeConnection]] = None
    pass


class VFNodeFlag(Flag):
    isNested = 0x01
    isAttached = 0x02
    isTask = 0x04
    isPassive = 0x08
    pass


class VFNodeAttaching(BaseModel):
    type: str
    pos: List[Union[str, int]]
    label: str
    pass


class VFNodeAttachedNode(BaseModel):
    nid: str
    pass


class VFNodePadding(BaseModel):
    top: int
    bottom: int
    left: int
    right: int
    gap: Optional[int] = None


class VFNodeSize(BaseModel):
    width: float
    height: float


class VFNodeNesting(BaseModel):
    pad: VFNodePadding
    attached_pad: VFNodePadding
    attached_nodes: Dict[VFNodeConnectionDataAttachedType, VFNodeAttachedNode]


class VFNodeData(BaseModel):
    ntype: str
    vtype: str
    flag: VFNodeFlag
    label: str
    placeholderlabel: str
    size: Optional[VFNodeSize] = None
    min_size: Optional[VFNodeSize] = None
    attaching: Optional[VFNodeAttaching] = None
    nesting: Optional[VFNodeNesting] = None
    connections: Optional[VFNodeConnections] = None
    payloads: Optional[VFNodeContents] = None
    results: Optional[VFNodeContents] = None
    pass

    def get(self, path: List[str]):
        pass

    def getContent(self, content_name: str) -> VFNodeContents:
        if content_name == "payloads":
            return self.payloads
        elif content_name == "results":
            return self.results


class VFNodePosition(BaseModel):
    x: float
    y: float
    pass


class VFNodeInfo(BaseModel):
    id: str
    type: str
    position: VFNodePosition
    data: VFNodeData
    parentNode: Optional[str] = None
    pass


class VFEdgeInfo(BaseModel):
    id: str
    type: str
    source: str
    target: str
    sourceHandle: str
    targetHandle: str
    data: dict
    label: str
    pass


class VFlowData(BaseModel):
    nodes: List[VFNodeInfo]
    edges: List[VFEdgeInfo]
    pass

import asyncio
import uuid
from typing import List, Any, Dict, Optional, Union
from enum import Enum, Flag
from pydantic import BaseModel
import json
from app.utils.vueRef import RefType
from app.schemas.VFNodeInterface import VFNodeData


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

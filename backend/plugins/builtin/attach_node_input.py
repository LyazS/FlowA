from typing import List, Dict, Optional, TYPE_CHECKING, Any
from app.schemas.VFNodeClass import VFNode
from app.schemas.vfnode import VFNodeInfo
from app.nodes.BaseNode import FABaseNode
from app.nodes.TaskNode import FATaskNode
from app.uisdk import *
from app.schemas.VFNodeClass import VFNode
from app.schemas.VFNodeInterface import (
    VFNodeConnectionType,
    VFNodeFlag,
    VFNodeContentData,
    VFNodeHandleData,
    VFNodeConnectionDataType,
    VFNodeAttachingType,
    VFNodeAttachingPos,
    VFNodeAttachingPosType,
)

if TYPE_CHECKING:
    from app.services.FARunner import FARunner


class ExamNode(FATaskNode):
    def __init__(self, wid: str, nodeinfo: VFNodeInfo, runner: "FARunner"):
        super().__init__(wid, nodeinfo, runner)
        pass

    def getCacheKey(self, request_nid: str):
        if pNode := self.runner().getNode(self.parentNode):
            return pNode.getCacheKey(request_nid)
        return None
        pass

    @staticmethod
    async def getNodeConfig():
        return {}

    @staticmethod
    def getNodeCreateInfo():
        thisnode = VFNode("attached_node")
        thisnode.set_flag(VFNodeFlag.IsAttached)
        thisnode.set_size(20, 6)
        thisnode.init_as_attached_node(
            VFNodeAttachingType.Input,
            VFNodeAttachingPos(
                XType=VFNodeAttachingPosType.Left,
                XOffset=0,
                YType=VFNodeAttachingPosType.Top,
                YOffset=0,
            ),
            "INPUT",
        )
        thisnode.add_handle(VFNodeConnectionType.Outputs, "output", "Output")
        thisnode.add_handle_data(
            VFNodeConnectionType.Outputs,
            "output",
            VFNodeHandleData(
                Type=VFNodeConnectionDataType.FromParent,
                HandleId="Attach",
            ),
        )
        return thisnode


# 必须存在
EXPORT_NODE = ExamNode

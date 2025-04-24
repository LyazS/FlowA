from typing import List, Dict, Optional, TYPE_CHECKING, Any
from app.schemas.VFNodeClass import VFNode
from app.schemas.VFlowData import VFNodeInfo
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
from app.services.FARunner import FARunner


class AttachNode(FATaskNode):
    def __init__(self, wid: str, nodeinfo: VFNodeInfo, runner: "FARunner"):
        super().__init__(wid, nodeinfo, runner)
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
            VFNodeAttachingType.Output,
            VFNodeAttachingPos(
                XType=VFNodeAttachingPosType.Right,
                XOffset=0,
                YType=VFNodeAttachingPosType.Bottom,
                YOffset=1,
            ),
            "BREAK",
        )
        thisnode.add_handle(VFNodeConnectionType.Inputs, "input")
        thisnode.add_handle(VFNodeConnectionType.Self, "self")
        thisnode.add_handle_data(
            VFNodeConnectionType.Self,
            "self",
            VFNodeHandleData(
                Type=VFNodeConnectionDataType.FromOuter,
                HandleId="input",
            ),
        )
        return thisnode


# 必须存在
EXPORT_NODE = AttachNode

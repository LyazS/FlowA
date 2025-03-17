from typing import List, Dict, Optional, TYPE_CHECKING, Any
from app.schemas.VFNodeClass import VFNode
from app.schemas.vfnode import VFNodeInfo
from app.schemas.fanode import FANodeValidateNeed
from app.nodes.basenode import FABaseNode
from app.nodes.tasknode import FATaskNode
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
        self.validateNeededs: List[FANodeValidateNeed] = [FANodeValidateNeed.Self]
        pass

    @staticmethod
    def getNodeConfig():
        return {}

    @staticmethod
    def getNodeCreateInfo():
        thisnode = VFNode("exam_nest_node", "basenode", "Exam Nest Node")
        thisnode.set_flag(VFNodeFlag.IsTask | VFNodeFlag.IsNested)
        thisnode.set_size(200, 200)

        thisnode.add_attached_node("ainput", "attached_node_input")
        thisnode.add_attached_node("aoutput", "attached_node_output")

        thisnode.add_handle(VFNodeConnectionType.Inputs, "input", "Input")
        thisnode.add_handle(VFNodeConnectionType.Outputs, "output", "Output")
        thisnode.add_handle(VFNodeConnectionType.Self, "Self")
        thisnode.add_handle(VFNodeConnectionType.Self, "AttachOutput")
        thisnode.add_handle(VFNodeConnectionType.Attach, "Attach")

        thisnode.add_handle_data(
            VFNodeConnectionType.Self,
            "Self",
            VFNodeHandleData(
                Type=VFNodeConnectionDataType.FromOuter,
                InputKey="input",
            ),
        )
        thisnode.add_handle_data(
            VFNodeConnectionType.Self,
            "AttachOutput",
            VFNodeHandleData(
                Type=VFNodeConnectionDataType.FromAttached,
                AName="aoutput",
            ),
        )
        thisnode.add_handle_data(
            VFNodeConnectionType.Attach,
            "Attach",
            VFNodeHandleData(
                Type=VFNodeConnectionDataType.FromAttached,
                AName="aoutput",
            ),
        )

        return thisnode


# 必须存在
EXPORT_NODE = ExamNode

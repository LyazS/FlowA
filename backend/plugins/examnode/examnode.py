from typing import List, Dict, Optional, TYPE_CHECKING, Any
from app.schemas.VFNodeClass import VFNode
from app.schemas.vfnode import VFNodeInfo
from app.schemas.fanode import FANodeValidateNeed
from app.nodes.basenode import FABaseNode
from app.uisdk import *
from app.schemas.VFNodeClass import VFNode
from app.schemas.VFNodeInterface import (
    VFNodeConnectionType,
    VFNodeFlag,
    VFNodeContentData,
    VFNodeHandleData,
    VFNodeConnectionDataType,
)

if TYPE_CHECKING:
    from app.services.FARunner import FARunner


class ExamNode(FABaseNode):
    def __init__(self, wid: str, nodeinfo: VFNodeInfo, runner: "FARunner"):
        super().__init__(wid, nodeinfo, runner)
        self.validateNeededs: List[FANodeValidateNeed] = [FANodeValidateNeed.Self]
        pass

    @staticmethod
    def getNodeConfig():
        return {}

    @staticmethod
    def getNodeCreateInfo():
        thisnode = VFNode("examnode", "examnode", "Exam Node")
        thisnode.set_flag(VFNodeFlag.IsTask)
        thisnode.set_size(80, 80)
        thisnode.add_handle(VFNodeConnectionType.Inputs, "input", "Input")
        thisnode.add_handle(VFNodeConnectionType.Outputs, "output", "Output")

        thisnode.add_payload(
            VFNodeContentData(
                Label="文本内容",
                Type="String",
                Key="text",
                Data="Hello World",
                UiType="UI_TEXT_INPUT",
            ),
            payload_id="D_EXAM_TEXT",
        )
        thisnode.add_handle_data(
            VFNodeConnectionType.Outputs,
            "output",
            VFNodeHandleData(
                Type=VFNodeConnectionDataType.FromInner,
                Path=["Payloads", "ById", "D_EXAM_TEXT"],
            ),
        )
        return thisnode.model_dump_json()


# 必须存在
EXPORT_NODE = ExamNode

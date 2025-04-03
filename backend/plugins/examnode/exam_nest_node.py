from typing import List, Dict, Optional, TYPE_CHECKING, Any
from app.schemas.VFNodeClass import VFNode
from app.schemas.vfnode import VFNodeInfo
from app.schemas.fanode import FANodeValidateNeed
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
    VFNodeHandleDataANode,
)

if TYPE_CHECKING:
    from app.services.FARunner import FARunner


class ExamNestNode(FATaskNode):
    def __init__(self, wid: str, nodeinfo: VFNodeInfo, runner: "FARunner"):
        super().__init__(wid, nodeinfo, runner)
        pass

    @staticmethod
    def getNodeConfig():
        return {}

    @staticmethod
    def getNodeCreateInfo():
        thisnode = VFNode("basenode")
        thisnode.set_flag(VFNodeFlag.IsTask)
        thisnode.init_as_nested_node("EXAM")
        thisnode.set_size(200, 200)

        thisnode.add_attached_node("ainput", "@/FlowABuiltin/attach_node_input")
        thisnode.add_attached_node("aoutput", "@/FlowABuiltin/attach_node_output")

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
                HandleId="input",
            ),
        )
        thisnode.add_handle_data(
            VFNodeConnectionType.Self,
            "AttachOutput",
            VFNodeHandleData(
                Type=VFNodeConnectionDataType.FromAttached,
                ANode={
                    "aoutput": VFNodeHandleDataANode(
                        ConnectionType=VFNodeConnectionType.Self,
                        HandleId="self",
                    )
                },
            ),
        )

        thisnode.add_payload(
            VFNodeContentData(
                Label="测试vfor",
                Type="List",
                # Key="items",
                Data=[],
                UiType="@/Exam Provider/TEST_VFOR_ITEMS",
            ),
            payload_id="TEST_VFOR_ITEMS",
        )
        thisnode.add_payload(
            VFNodeContentData(
                Label="文本内容",
                Type="String",
                # Key="text",
                Data="Hello World",
                UiType="@/Exam Provider/UI_TEXT_INPUT",
            ),
            payload_id="D_EXAM_TEXT",
        )
        thisnode.add_handle_data(
            VFNodeConnectionType.Attach,
            "Attach",
            VFNodeHandleData(
                Type=VFNodeConnectionDataType.FromInner,
                Path=["Payloads", "ById", "D_EXAM_TEXT", "Data"],
            ),
        )
        thisnode.add_handle_data(
            VFNodeConnectionType.Attach,
            "Attach",
            VFNodeHandleData(
                Type=VFNodeConnectionDataType.FromOuter,
                HandleId="input",
            ),
        )

        return thisnode


# 必须存在
EXPORT_NODE = ExamNestNode

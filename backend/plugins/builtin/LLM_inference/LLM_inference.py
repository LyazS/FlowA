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
    VFNodeContentDataConfig,
)

if TYPE_CHECKING:
    from app.services.FARunner import FARunner

from ..UI_Components.UI_InputVars import DefaultInputVar


class LLMInference(FATaskNode):
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
        thisnode.set_size(80, 80)
        thisnode.add_handle(VFNodeConnectionType.Inputs, "input", "Input")
        thisnode.add_handle(VFNodeConnectionType.Outputs, "output", "Output")
        thisnode.add_handle(VFNodeConnectionType.Self, "self")
        thisnode.add_handle_data(
            VFNodeConnectionType.Self,
            "self",
            VFNodeHandleData(
                Type=VFNodeConnectionDataType.FromOuter,
                HandleId="input",
            ),
        )
        thisnode.add_payload(
            VFNodeContentData(
                Label="模型设置",
                Type="Dict",
                Data={
                    "Model": {
                        "Label": "模型",
                        "Type": "Const",
                        "Content": "deepseek-chat",
                    },
                    "MaxTokens": {
                        "Label": "流式输出",
                        "Type": "Const",
                        "Content": True,
                    },
                },
                UiType="@/FlowABuiltin/UI_CODE_EDITOR",
            ),
            payload_id="D_MODEL_SETTING",
        )
        thisnode.add_payload(
            VFNodeContentData(
                Label="输入变量",
                Type="List",
                Data=[
                    DefaultInputVar(key="arg1", valueStr="good"),
                    DefaultInputVar(key="arg2", valueStr="assistant"),
                ],
                UiType="@/FlowABuiltin/UI_INPUT_VARS",
            ),
            payload_id="D_INPUT_VARS",
        )

        thisnode.add_result_into_outputs(
            VFNodeContentData(
                Label="output1",
                Type="String",
                # Key="output",
                Data="",
            ),
            handle_id="output",
        )
        thisnode.set_outputs_ui_type("@/FlowABuiltin/UI_CODE_OUTPUT")
        return thisnode


# 必须存在
EXPORT_NODE = LLMInference

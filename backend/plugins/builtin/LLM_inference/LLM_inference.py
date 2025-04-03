from typing import List, Dict, Optional, TYPE_CHECKING, Any, Literal
from pydantic import BaseModel
from enum import StrEnum
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
    VFNodeContentDataConfig,
)

if TYPE_CHECKING:
    from app.services.FARunner import FARunner

from ..UI_Components.UI_InputVars import InputVarModel


class LLMSettingType(StrEnum):
    Const = "Const"
    Null = "Null"
    Ref = "Ref"


class LLMSetting(BaseModel):
    Label: str
    Type: LLMSettingType
    Content: Any


class LLMSettings(BaseModel):
    Model: LLMSetting
    Stream: LLMSetting
    MaxTokens: LLMSetting
    Temperature: LLMSetting
    TopP: LLMSetting
    FrequencyPenalty: LLMSetting
    ResponseFormat: LLMSetting
    Stop: LLMSetting


class LLMRole(StrEnum):
    system = "system"
    user = "user"
    assistant = "assistant"
    pass


class SinglePrompt(BaseModel):
    role: LLMRole
    content: str
    pass


LLMTypeOptions: List[SelectOptions] = [
    SelectOptions(label="引用", value=LLMSettingType.Ref),
    SelectOptions(label="常量", value=LLMSettingType.Const),
]
LLMTypeOptionsWnull: List[SelectOptions] = [
    SelectOptions(label="引用", value=LLMSettingType.Ref),
    SelectOptions(label="常量", value=LLMSettingType.Const),
    SelectOptions(label="缺省", value=LLMSettingType.Null),
]
LLMRoleOptions: List[SelectOptions] = [
    SelectOptions(label="System", value=LLMRole.system),
    SelectOptions(label="User", value=LLMRole.user),
    SelectOptions(label="Assistant", value=LLMRole.assistant),
]


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
        thisnode.add_handle(VFNodeConnectionType.Outputs, "output_res", "RESULT")
        thisnode.add_handle(VFNodeConnectionType.Outputs, "output_info", "INFO")
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
                Data=LLMSettings(
                    Model=LLMSetting(
                        Label="模型选择",
                        Type=LLMSettingType.Const,
                        Content="deepseek-chat",
                    ),
                    Stream=LLMSetting(
                        Label="流式输出",
                        Type=LLMSettingType.Const,
                        Content=True,
                    ),
                    MaxTokens=LLMSetting(
                        Label="最大输出",
                        Type=LLMSettingType.Null,
                        Content=4096,
                    ),
                    Temperature=LLMSetting(
                        Label="温度调整",
                        Type=LLMSettingType.Null,
                        Content=0.75,
                    ),
                    TopP=LLMSetting(
                        Label="Top   P",
                        Type=LLMSettingType.Null,
                        Content=0.9,
                    ),
                    FrequencyPenalty=LLMSetting(
                        Label="频率惩罚",
                        Type=LLMSettingType.Null,
                        Content=0.5,
                    ),
                    ResponseFormat=LLMSetting(
                        Label="回复格式",
                        Type=LLMSettingType.Null,
                        Content="json",
                    ),
                    Stop=LLMSetting(
                        Label="停止标记",
                        Type=LLMSettingType.Null,
                        Content="",
                    ),
                ),
                UiType="@/FlowABuiltin/UI_LLM_SETTINGS",
            ),
            payload_id="D_MODEL_SETTING",
        )
        thisnode.add_payload(
            VFNodeContentData(
                Label="输入变量",
                Type="List",
                Data=[
                    InputVarModel(key="arg1", valueStr="good"),
                    InputVarModel(key="arg2", valueStr="assistant"),
                ],
                UiType="@/FlowABuiltin/UI_INPUT_VARS",
            ),
            payload_id="D_INPUT_VARS",
        )
        thisnode.add_payload(
            VFNodeContentData(
                Label="Prompts设计",
                Type="List",
                Data=[
                    SinglePrompt(
                        role=LLMRole.system, content="You ara a {{arg1}} {{arg2}}."
                    ),
                    SinglePrompt(role=LLMRole.user, content="Hi."),
                ],
                UiType="@/FlowABuiltin/UI_LLM_PROMPTS",
            ),
            payload_id="D_PROMPTS",
        )

        thisnode.add_result_into_outputs(
            VFNodeContentData(
                Label="推理结果",
                Type="String",
                Data="",
            ),
            handle_id="output_res",
            result_id="D_ANSWER",
        )
        thisnode.add_result_into_outputs(
            VFNodeContentData(
                Label="LLM模型",
                Type="String",
                Data="",
            ),
            handle_id="output_info",
            result_id="D_MODEL",
        )
        thisnode.add_result_into_outputs(
            VFNodeContentData(
                Label="输入Token",
                Type="Integer",
                Data=0,
            ),
            handle_id="output_info",
            result_id="D_IN_TOKEN",
        )
        thisnode.add_result_into_outputs(
            VFNodeContentData(
                Label="输出Token",
                Type="Integer",
                Data=0,
            ),
            handle_id="output_info",
            result_id="D_OUT_TOKEN",
        )
        thisnode.add_result_into_outputs(
            VFNodeContentData(
                Label="停止原因",
                Type="String",
                Data="",
            ),
            handle_id="output_info",
            result_id="D_STOP_REASON",
        )

        thisnode.set_outputs_ui_type("@/FlowABuiltin/UI_TAG_OUTPUTS")
        return thisnode


# 必须存在
EXPORT_NODE = LLMInference

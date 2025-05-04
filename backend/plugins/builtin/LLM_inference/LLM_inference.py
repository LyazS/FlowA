from typing import List, Dict, Optional, TYPE_CHECKING, Any, Literal, Union, cast
from pydantic import BaseModel
from enum import StrEnum
import os
import json
import asyncio
import traceback
from loguru import logger
from decimal import Decimal
import openai
from openai import AsyncOpenAI, NotGiven
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionChunk,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam,
    ChatCompletionToolMessageParam,
    ChatCompletionFunctionMessageParam,
    ChatCompletionContentPartParam,
    ChatCompletionContentPartTextParam,
    ChatCompletionContentPartImageParam,
    ChatCompletionContentPartInputAudioParam,
)
from app.schemas.VFNodeClass import VFNode
from app.schemas.VFlowData import VFNodeInfo
from app.schemas.VFlowRunData import FARunStatus
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
    VarType,
    RefVarItem,
)
from app.schemas.farequest import (
    ValidationError,
    FANodeUpdateType,
    FANodeUpdateData,
)
from app.utils.tools import read_yaml, reduceGet, replace_vars
from app.utils.db4node import loadNodeConfig, setNodeConfig
from app.services.FARunner import FARunner
from app.services.FAValidator import FAValidator
from ..UI_Components.UI_InputVars import InputVarModel


class LLMSettingType(StrEnum):
    Const = "Const"
    Null = "Null"
    Ref = "Ref"


class LLMSetting(BaseModel):
    Label: str
    Type: LLMSettingType
    Content: Any
    ContentRef: Optional[RefVarItem] = None


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


class LLMPromptType(StrEnum):
    text = "text"
    image_url = "image_url"


class LLMPromptImageDetail(StrEnum):
    auto = "auto"
    low = "low"
    high = "high"


class LLMPromptImageParamType(StrEnum):
    FromUpload = "FromUpload"
    FromRef = "FromRef"


class LLMPromptImageURL(BaseModel):
    # Either a URL of the image or the base64 encoded image data.
    url: Optional[ReadOnlyPropVar] = None
    detail: LLMPromptImageDetail
    urlRef: Optional[RefVarItem] = None
    urlType: LLMPromptImageParamType
    pass


class LLMPromptImageParam(BaseModel):
    type: LLMPromptType = LLMPromptType.image_url
    image_url: LLMPromptImageURL
    pass


class LLMPromptTextParam(BaseModel):
    type: LLMPromptType = LLMPromptType.text
    text: str


class LLMPrompt(BaseModel):
    role: LLMRole
    content: List[Union[LLMPromptImageParam, LLMPromptTextParam]]
    pass


class LLMModel(BaseModel):
    name: str
    # max_input_tokens: Decimal
    # max_output_tokens: Decimal
    # prompt: Decimal
    # complete: Decimal
    # rate: Decimal
    # capability: List[str]
    pass


THIS_NODE_NAME = "@FALLMInference"
NODE_CONFIG = {}
BASE_URL = None
API_KEY = None
MODELS = None
MODELS_SELECT = None
AsyncOAIClient = None


async def init_node_class():
    global NODE_CONFIG
    global BASE_URL
    global API_KEY
    global MODELS
    global MODELS_SELECT
    global AsyncOAIClient
    ret, config = await loadNodeConfig(THIS_NODE_NAME)
    if ret:
        NODE_CONFIG = config
    else:
        NODE_CONFIG = read_yaml(
            os.path.join(
                os.path.dirname(__file__),
                "FANode_LLM_inference.yaml",
            )
        )
        await setNodeConfig(THIS_NODE_NAME, NODE_CONFIG)
    BASE_URL = NODE_CONFIG["base_url"]
    API_KEY = NODE_CONFIG["api_key"]
    MODELS = {
        m["name"]: LLMModel(
            name=m["name"],
            # max_input_tokens=Decimal(m["max_input_tokens"]),
            # max_output_tokens=Decimal(m["max_output_tokens"]),
            # prompt=Decimal(m["prompt"]),
            # complete=Decimal(m["complete"]),
            # rate=Decimal(m["rate"]),
            # capability=m["capability"],
        )
        for m in NODE_CONFIG["models"]
    }
    MODELS_SELECT = [
        SelectOptions(label=m["name"], value=m["name"]) for m in NODE_CONFIG["models"]
    ]
    AsyncOAIClient = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
    await LLMInference.getNodeConfig()
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

    def validateConfigVar(self, s_config: LLMSetting, selfVars):
        if s_config.Type == LLMSettingType.Ref:
            if (
                not s_config.ContentRef
                or s_config.ContentRef.model_dump_json() in selfVars
            ):
                return True
            else:
                return False
            pass

        return True

    async def validate(self, validator: "FAValidator") -> Optional[ValidationError]:
        error_msgs = []
        try:
            selfVars = await validator.getConnectionByPath(
                self.id,
                [
                    CONNECT_DATA_TO_SELECT,
                    VFNodeConnectionType.Self,
                    "self",
                ],
            )
            node_payloads = self.data.Payloads

            UI_INPUT_VARS: VFNodeContentData = node_payloads.ById["D_INPUT_VARS"]
            for var_dict in UI_INPUT_VARS.Data.value:
                var = InputVarModel.model_validate(var_dict)
                if var.Type == VarType.Ref and (
                    not var.ValueRef or var.ValueRef.model_dump_json() not in selfVars
                ):
                    error_msgs.append(f"变量未定义{var.ValueRef}")
            D_MODEL_SETTING: VFNodeContentData = node_payloads.ById["D_MODEL_SETTING"]
            model_cfg = LLMSettings.model_validate(D_MODEL_SETTING.Data.value)

            if not self.validateConfigVar(model_cfg.Model, selfVars):
                error_msgs.append(f"模型配置变量{model_cfg.Model.ContentRef}未定义")
            elif model_cfg.Model.Type == LLMSettingType.Const:
                cfg_model = model_cfg.Model.Content
                if cfg_model not in MODELS:
                    error_msgs.append(f"模型{cfg_model}不在支持列表中")
            if not self.validateConfigVar(model_cfg.MaxTokens, selfVars):
                error_msgs.append(f"模型配置变量{model_cfg.MaxTokens.ContentRef}未定义")
            if not self.validateConfigVar(model_cfg.Temperature, selfVars):
                error_msgs.append(
                    f"模型配置变量{model_cfg.Temperature.ContentRef}未定义"
                )
            if not self.validateConfigVar(model_cfg.TopP, selfVars):
                error_msgs.append(f"模型配置变量{model_cfg.TopP.ContentRef}未定义")
            if not self.validateConfigVar(model_cfg.FrequencyPenalty, selfVars):
                error_msgs.append(
                    f"模型配置变量{model_cfg.FrequencyPenalty.ContentRef}未定义"
                )
            if not self.validateConfigVar(model_cfg.ResponseFormat, selfVars):
                error_msgs.append(
                    f"模型配置变量{model_cfg.ResponseFormat.ContentRef}未定义"
                )

        except Exception as e:
            errmsg = traceback.format_exc()
            error_msgs.append(f"获取内容失败{str(errmsg)}")

        if len(error_msgs) > 0:
            return ValidationError(nid=self.id, errors=error_msgs)
        return None

    async def getConfigVar(self, s_config: LLMSetting):
        if s_config.Type == LLMSettingType.Ref:
            return await InputVarModel.get_value(
                InputVarModel(
                    Key="",
                    Type=VarType.Ref,
                    ValueRef=s_config.ContentRef,
                ),
                self.id,
                self.runner().getRefData,
            )
            pass
        elif s_config.Type == LLMSettingType.Const:
            return s_config.Content
        elif s_config.Type == LLMSettingType.Null:
            return NotGiven
        return NotGiven

    async def run(self) -> List[FANodeUpdateData]:
        for try_count in range(5):
            try:
                node_payloads = self.data.Payloads
                node_results = self.data.Results
                D_INPUT_VARS: VFNodeContentData = node_payloads.ById["D_INPUT_VARS"]
                D_MODEL_SETTING: VFNodeContentData = node_payloads.ById[
                    "D_MODEL_SETTING"
                ]
                D_PROMPTS: VFNodeContentData = node_payloads.ById["D_PROMPTS"]
                D_ANSWER: VFNodeContentData = node_results.ById["D_ANSWER"]
                D_THOUGHT: VFNodeContentData = node_results.ById["D_THOUGHT"]
                D_MODEL: VFNodeContentData = node_results.ById["D_MODEL"]
                D_IN_TOKEN: VFNodeContentData = node_results.ById["D_IN_TOKEN"]
                D_OUT_TOKEN: VFNodeContentData = node_results.ById["D_OUT_TOKEN"]
                D_STOP_REASON: VFNodeContentData = node_results.ById["D_STOP_REASON"]
                InputArgs = {}
                for var_dict in D_INPUT_VARS.Data.value:
                    var = InputVarModel.model_validate(var_dict)
                    InputArgs[var.Key] = await InputVarModel.get_value(
                        var,
                        self.id,
                        self.runner().getRefData,
                    )
                model_cfg = LLMSettings.model_validate(D_MODEL_SETTING.Data.value)
                isStream = await self.getConfigVar(model_cfg.Stream)
                model_name = await self.getConfigVar(model_cfg.Model)
                if model_name not in MODELS:
                    raise Exception(f"模型{model_name}不在支持列表中")
                completions_params = {
                    "model": model_name,
                    "stream": isStream,
                    "max_tokens": await self.getConfigVar(model_cfg.MaxTokens),
                    "temperature": await self.getConfigVar(model_cfg.Temperature),
                    "top_p": await self.getConfigVar(model_cfg.Temperature),
                    # "top_k": await self.getConfigVar(model_cfg.top_k),
                    "frequency_penalty": await self.getConfigVar(
                        model_cfg.FrequencyPenalty
                    ),
                }
                if isStream:
                    completions_params["stream_options"] = {"include_usage": True}
                    pass
                isJson = await self.getConfigVar(model_cfg.ResponseFormat) == "json"
                if isJson:
                    completions_params["response_format"] = {"type": "json_object"}
                # messages
                messages = []
                for prompt in D_PROMPTS.Data.value:
                    prompt_obj = LLMPrompt.model_validate(prompt)
                    prompt_obj.content = replace_vars(prompt_obj.content, InputArgs)
                    messages.append(json.loads(prompt_obj.model_dump_json()))
                    pass
                completions_params["messages"] = messages
                completions_params = {
                    k: v for k, v in completions_params.items() if v is not NotGiven
                }
                chat_completion: ChatCompletion = await AsyncOAIClient.with_options(
                    max_retries=10
                ).chat.completions.create(**completions_params)
                D_ANSWER.Data.value = ""
                D_THOUGHT.Data.value = ""
                if isStream:
                    async for chunk in chat_completion:
                        chunk = cast(ChatCompletionChunk, chunk)
                        if len(chunk.choices) > 0:
                            content = chunk.choices[0].delta.content
                            if content is not None:
                                D_ANSWER.Data.value += content
                            reasoning_content = chunk.choices[0].delta.model_extra.get(
                                "reasoning_content", None
                            )
                            if reasoning_content is not None:
                                D_THOUGHT.Data.value += reasoning_content
                            D_STOP_REASON.Data.value = chunk.choices[0].finish_reason
                            pass
                        if chunk.usage is not None:
                            D_IN_TOKEN.Data.value = chunk.usage.prompt_tokens
                            D_OUT_TOKEN.Data.value = chunk.usage.completion_tokens
                            pass
                else:
                    D_ANSWER.Data.value = chat_completion.choices[0].message.content
                    D_THOUGHT.Data.value = chat_completion.choices[
                        0
                    ].message.model_extra.get("reasoning_content", None)
                    D_IN_TOKEN.Data.value = chat_completion.usage.prompt_tokens
                    D_OUT_TOKEN.Data.value = chat_completion.usage.completion_tokens
                    D_STOP_REASON.Data.value = chat_completion.choices[0].finish_reason
                    pass
                D_MODEL.Data.value = completions_params["model"]
                logger.info(
                    f"补全Tokens：{D_IN_TOKEN.Data.value} + {D_OUT_TOKEN.Data.value}"
                )
                if isJson:
                    json.loads(D_ANSWER.Data.value)
                self.setAllOutputStatus(FARunStatus.Success)
                return
            except json.JSONDecodeError:
                if try_count >= 5:
                    raise Exception(f"JSON格式错误：{D_ANSWER.Data.value}")
                else:
                    logger.warning(f"正在重试，因为JSON格式错误：{D_ANSWER.Data.value}")
                    await asyncio.sleep(2**try_count)
                    continue
                pass
            except openai.APIConnectionError as e:
                errmsg = traceback.format_exc()
                if try_count >= 5:
                    raise Exception(f"LLM节点运行失败：{errmsg}")
                else:
                    logger.warning(f"正在重试，因为API连接错误：{errmsg}")
                    await asyncio.sleep(2**try_count)
                    continue
                pass
            except openai.RateLimitError as e:
                errmsg = traceback.format_exc()
                if try_count >= 5:
                    raise Exception(f"LLM节点运行失败：{errmsg}")
                else:
                    logger.warning(f"正在重试，因为API请求频率限制：{errmsg}")
                    await asyncio.sleep(2**try_count)
                    continue
                pass
            except openai.APIStatusError as e:
                errmsg = traceback.format_exc()
                if try_count >= 5:
                    raise Exception(f"LLM节点运行失败：{errmsg}")
                else:
                    logger.warning(f"正在重试，因为API状态错误：{errmsg}")
                    await asyncio.sleep(2**try_count)
                    continue
                pass
            except Exception as e:
                errmsg = traceback.format_exc()
                logger.warning(f"LLM节点运行失败：{errmsg}")
                raise Exception(f"LLM节点运行失败：{errmsg}")
            pass

    @staticmethod
    async def getNodeConfig():
        global MODELS
        global MODELS_SELECT
        modellist = (await AsyncOAIClient.models.list()).data
        MODELS_SELECT = [SelectOptions(label=m.id, value=m.id) for m in modellist]
        MODELS_SELECT = sorted(MODELS_SELECT, key=lambda x: x.label.lower())
        MODELS = {
            m.id: LLMModel(
                name=m.id,
                # max_input_tokens=Decimal(0),
                # max_output_tokens=Decimal(0),
                # prompt=Decimal(0),
                # complete=Decimal(0),
                # rate=Decimal(1.0),
                # capability=[],
            )
            for m in modellist
        }
        return {
            "models": MODELS,
            "models_select": MODELS_SELECT,
        }

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
                Type=VarType.Dict,
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
                Type=VarType.List,
                Data=[
                    InputVarModel(Key="arg1", ValueStr="good"),
                    InputVarModel(Key="arg2", ValueStr="assistant"),
                ],
                UiType="@/FlowABuiltin/UI_INPUT_VARS",
            ),
            payload_id="D_INPUT_VARS",
        )
        thisnode.add_payload(
            VFNodeContentData(
                Label="Prompts设计",
                Type=VarType.List,
                Data=[
                    LLMPrompt(
                        role=LLMRole.system,
                        content=[
                            LLMPromptTextParam(text="You ara a {{arg1}} {{arg2}}.")
                        ],
                    ),
                    LLMPrompt(
                        role=LLMRole.user,
                        content=[LLMPromptTextParam(text="Hi.")],
                    ),
                ],
                UiType="@/FlowABuiltin/UI_LLM_PROMPTS",
            ),
            payload_id="D_PROMPTS",
        )

        thisnode.add_result_into_outputs(
            VFNodeContentData(
                Label="思考结果",
                Type=VarType.String,
                Data="",
            ),
            handle_id="output_res",
            result_id="D_THOUGHT",
        )
        thisnode.add_result_into_outputs(
            VFNodeContentData(
                Label="推理结果",
                Type=VarType.String,
                Data="",
            ),
            handle_id="output_res",
            result_id="D_ANSWER",
        )
        thisnode.add_result_into_outputs(
            VFNodeContentData(
                Label="LLM模型",
                Type=VarType.String,
                Data="",
            ),
            handle_id="output_info",
            result_id="D_MODEL",
        )
        thisnode.add_result_into_outputs(
            VFNodeContentData(
                Label="输入Token",
                Type=VarType.Integer,
                Data=0,
            ),
            handle_id="output_info",
            result_id="D_IN_TOKEN",
        )
        thisnode.add_result_into_outputs(
            VFNodeContentData(
                Label="输出Token",
                Type=VarType.Integer,
                Data=0,
            ),
            handle_id="output_info",
            result_id="D_OUT_TOKEN",
        )
        thisnode.add_result_into_outputs(
            VFNodeContentData(
                Label="停止原因",
                Type=VarType.String,
                Data="",
            ),
            handle_id="output_info",
            result_id="D_STOP_REASON",
        )

        thisnode.set_outputs_ui_type("@/FlowABuiltin/UI_TAG_OUTPUTS")
        return thisnode


# 必须存在
EXPORT_NODE = LLMInference
# 可选存在
EXPORT_INIT = init_node_class

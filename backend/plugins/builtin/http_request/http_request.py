from typing import List, Dict, Optional, TYPE_CHECKING, Any, Union, Literal
import asyncio
import os
import re
import ast
import copy
import sys
import json
import traceback
import base64
from loguru import logger
from enum import StrEnum
from pydantic import BaseModel
from app.schemas.VFNodeClass import VFNode
from app.schemas.VFlowData import VFNodeInfo
from app.schemas.VFlowRunData import FARunStatus
from app.schemas.farequest import (
    ValidationError,
    FANodeUpdateType,
    FANodeUpdateData,
)
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
    FromInnerPath,
)
from app.utils.tools import read_yaml, reduceGet
from app.utils.db4node import loadNodeConfig, setNodeConfig
from app.services.FARunner import FARunner
from app.services.FAValidator import FAValidator
from ..UI_Components.UI_InputVars import InputVarModel, VarType


class HttpBaseDict(BaseModel):
    Key: str
    Value: str
    pass


class HttpRequestMethod(StrEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class HttpRequestConfig_URL(BaseModel):
    Method: HttpRequestMethod = HttpRequestMethod.GET
    Url: str = ""
    pass


class HttpRequestConfig_HEADER(HttpBaseDict):
    pass


class HttpRequestBodyType(StrEnum):
    NONE = "NONE"
    JSON = "JSON"
    TEXT = "TEXT"
    FORMDATA = "FORMDATA"
    XWWWFORMURL = "XWWWFORMURL"
    pass


class HttpRequestBody_XWWWFORMURL(HttpBaseDict):
    pass


class HttpRequestBody_FORMDATA(BaseModel):
    Type: Literal[VarType.String, VarType.File]
    pass


class HttpRequestConfig_BODY(BaseModel):
    Type: HttpRequestBodyType = HttpRequestBodyType.NONE
    Content1: str = ""
    Content2: List[HttpRequestBody_XWWWFORMURL] = []
    Content3: List[HttpRequestBody_FORMDATA] = []
    pass


class HttpRequestConfig_COOKIE(HttpBaseDict):
    pass


class HttpRequestConfig_TIMEOUT(BaseModel):
    Connect: float = 0
    Read: float = 0
    Write: float = 0
    pass


class HttpRequest(FATaskNode):
    def __init__(self, wid: str, nodeinfo: VFNodeInfo, runner: "FARunner"):
        super().__init__(wid, nodeinfo, runner)
        pass

    async def validate(self, validator: "FAValidator") -> Optional[ValidationError]:
        error_msgs = []
        try:
            pass
        except Exception as e:
            errmsg = traceback.format_exc()
            error_msgs.append(f"获取内容失败{str(errmsg)}")

        if len(error_msgs) > 0:
            return ValidationError(nid=self.id, errors=error_msgs)
        return None

    async def run(self) -> List[FANodeUpdateData]:
        pass

    @staticmethod
    async def getNodeConfig():
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
                Label="输入变量",
                Type="List",
                Data=[
                    InputVarModel(Key="query", ValueStr="say"),
                    InputVarModel(Key="ask", ValueStr="hi"),
                    InputVarModel(Key="token", ValueStr="xxx"),
                    InputVarModel(Key="cook", ValueStr="zzz"),
                ],
                UiType="@/FlowABuiltin/UI_INPUT_VARS",
            ),
            payload_id="D_INPUT_VARS",
        )
        thisnode.add_payload(
            VFNodeContentData(
                Label="请求 Method & URL",
                Type="Any",
                Data=HttpRequestConfig_URL(
                    Url="https://api.example.com?{{query}}={{ask}}"
                ),
                UiType="@/FlowABuiltin/UI_HTTP_URL",
            ),
            payload_id="D_URL",
        )

        thisnode.add_payload(
            VFNodeContentData(
                Label="请求头 Header",
                Type="List",
                Data=[
                    HttpRequestConfig_HEADER(
                        Key="Authorization", Value="Bearer {{token}}"
                    ),
                ],
                UiType="@/FlowABuiltin/UI_HTTP_HEADER",
            ),
            payload_id="D_HEADER",
        )

        thisnode.add_payload(
            VFNodeContentData(
                Label="请求体 Body",
                Type="Any",
                Data=HttpRequestConfig_BODY(),
                UiType="@/FlowABuiltin/UI_HTTP_BODY",
            ),
            payload_id="D_BODY",
        )

        thisnode.add_payload(
            VFNodeContentData(
                Label="Cookies",
                Type="List",
                Data=[
                    HttpRequestConfig_COOKIE(Key="cook", Value="{{cooker}}"),
                ],
                UiType="@/FlowABuiltin/UI_HTTP_COOKIE",
            ),
            payload_id="D_COOKIES",
        )

        thisnode.add_payload(
            VFNodeContentData(
                Label="超时配置",
                Type="Any",
                Data=HttpRequestConfig_TIMEOUT(),
                UiType="@/FlowABuiltin/UI_HTTP_TIMEOUT",
            ),
            payload_id="D_TIMEOUT",
        )

        thisnode.add_result_into_outputs(
            VFNodeContentData(
                Label="返回状态",
                Type="String",
                Data="",
            ),
            handle_id="output_info",
            result_id="DR_STATUS",
        )
        thisnode.add_result_into_outputs(
            VFNodeContentData(
                Label="返回头",
                Type="String",
                Data="",
            ),
            handle_id="output_info",
            result_id="DR_HEADER",
        )
        thisnode.add_result_into_outputs(
            VFNodeContentData(
                Label="返回Cookie",
                Type="String",
                Data="",
            ),
            handle_id="output_info",
            result_id="DR_COOKIE",
        )
        thisnode.add_result_into_outputs(
            VFNodeContentData(
                Label="返回类型",
                Type="String",
                Data="",
            ),
            handle_id="output_info",
            result_id="DR_CONTENTTYPE",
        )
        thisnode.add_result_into_outputs(
            VFNodeContentData(
                Label="返回结果",
                Type="String",
                Data="",
            ),
            handle_id="output_res",
            result_id="DR_RESPONSE",
        )

        thisnode.set_outputs_ui_type("@/FlowABuiltin/UI_TAG_OUTPUTS")
        return thisnode


# 必须存在
EXPORT_NODE = HttpRequest

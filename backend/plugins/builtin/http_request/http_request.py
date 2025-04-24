from typing import List, Dict, Optional, TYPE_CHECKING, Any, Union, Literal
import asyncio
import aiohttp
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
from app.utils.tools import read_yaml, reduceGet, replace_vars
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
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    TRACE = "TRACE"
    pass


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


class HttpRequestBody_FORMDATA(HttpBaseDict):
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


class HttpResponseFormat(StrEnum):
    TEXT = "TEXT"
    JSON = "JSON"
    BINARY = "BINARY"
    pass


class HttpRequest(FATaskNode):
    def __init__(self, wid: str, nodeinfo: VFNodeInfo, runner: "FARunner"):
        super().__init__(wid, nodeinfo, runner)
        pass

    async def validate(self, validator: "FAValidator") -> Optional[ValidationError]:
        error_msgs = []
        try:
            node_payloads = self.data.Payloads
            selfVars = await validator.getConnectionByPath(
                self.id,
                [
                    CONNECT_DATA_TO_SELECT,
                    VFNodeConnectionType.Self,
                    "self",
                ],
            )
            D_INPUT_VARS: VFNodeContentData = node_payloads.ById["D_INPUT_VARS"]
            for var_dict in D_INPUT_VARS.Data.value:
                var = InputVarModel.model_validate(var_dict)
                if var.Type == VarType.Ref and (
                    not var.ValueRef or var.ValueRef.model_dump_json() not in selfVars
                ):
                    error_msgs.append(f"没有该变量选项{var.ValueRef}")
            pass
            # 验证必要的配置项是否存在
            for payload_id in [
                "D_URL",
                "D_HEADER",
                "D_BODY",
                "D_COOKIES",
                "D_TIMEOUT",
                "D_RETURN_FORMAT",
            ]:
                if payload_id not in node_payloads.ById:
                    error_msgs.append(f"缺少必要的配置项: {payload_id}")
        except Exception as e:
            errmsg = traceback.format_exc()
            error_msgs.append(f"获取内容失败{str(errmsg)}")

        if len(error_msgs) > 0:
            return ValidationError(nid=self.id, errors=error_msgs)
        return None

    async def run(self) -> List[FANodeUpdateData]:
        node_payloads = self.data.Payloads
        D_INPUT_VARS: VFNodeContentData = node_payloads.ById["D_INPUT_VARS"]
        D_URL: VFNodeContentData = node_payloads.ById["D_URL"]
        D_HEADER: VFNodeContentData = node_payloads.ById["D_HEADER"]
        D_BODY: VFNodeContentData = node_payloads.ById["D_BODY"]
        D_COOKIES: VFNodeContentData = node_payloads.ById["D_COOKIES"]
        D_TIMEOUT: VFNodeContentData = node_payloads.ById["D_TIMEOUT"]
        D_RETURN_FORMAT: VFNodeContentData = node_payloads.ById["D_RETURN_FORMAT"]

        try:
            # 处理输入变量
            InputArgs = {}
            for var_dict in D_INPUT_VARS.Data.value:
                var = InputVarModel.model_validate(var_dict)
                InputArgs[var.Key] = await InputVarModel.get_value(
                    var,
                    self.id,
                    self.runner().getRefData,
                )

            # 处理URL和请求方法
            url_config = HttpRequestConfig_URL.model_validate(D_URL.Data.value)
            url = replace_vars(url_config.Url, InputArgs)
            method = url_config.Method

            # 处理请求头
            headers = {}
            for header_dict in D_HEADER.Data.value:
                header = HttpRequestConfig_HEADER.model_validate(header_dict)
                headers[header.Key] = replace_vars(header.Value, InputArgs)

            # 处理Cookies
            cookies = {}
            for cookie_dict in D_COOKIES.Data.value:
                cookie = HttpRequestConfig_COOKIE.model_validate(cookie_dict)
                cookies[cookie.Key] = replace_vars(cookie.Value, InputArgs)

            # 处理超时设置
            timeout_config = HttpRequestConfig_TIMEOUT.model_validate(
                D_TIMEOUT.Data.value
            )
            timeout = aiohttp.ClientTimeout(
                connect=timeout_config.Connect if timeout_config.Connect > 0 else None,
                sock_read=timeout_config.Read if timeout_config.Read > 0 else None,
                sock_connect=(
                    timeout_config.Connect if timeout_config.Connect > 0 else None
                ),
            )

            # 处理请求体
            body_config = HttpRequestConfig_BODY.model_validate(D_BODY.Data.value)
            body = None
            content_type = None

            if body_config.Type == HttpRequestBodyType.NONE:
                pass
            elif body_config.Type == HttpRequestBodyType.JSON:
                # JSON格式的请求体
                json_content = replace_vars(body_config.Content1, InputArgs)
                try:
                    body = json.loads(json_content)
                    content_type = "application/json"
                except json.JSONDecodeError:
                    raise Exception(f"JSON格式错误: {json_content}")
            elif body_config.Type == HttpRequestBodyType.TEXT:
                # 文本格式的请求体
                body = replace_vars(body_config.Content1, InputArgs)
                content_type = "text/plain"
            elif body_config.Type == HttpRequestBodyType.XWWWFORMURL:
                # x-www-form-urlencoded格式的请求体
                form_data = {}
                for item_dict in body_config.Content2:
                    item = HttpRequestBody_XWWWFORMURL.model_validate(item_dict)
                    form_data[replace_vars(item.Key, InputArgs)] = replace_vars(
                        item.Value, InputArgs
                    )
                body = form_data
                content_type = "application/x-www-form-urlencoded"
            elif body_config.Type == HttpRequestBodyType.FORMDATA:
                # multipart/form-data格式的请求体
                form_data = aiohttp.FormData()
                for item in body_config.Content3:
                    if item.Type == VarType.File:
                        # async with aiofiles.open(item["value"], "rb") as f:
                        #     data.add_field(
                        #         item["key"],
                        #         await f.read(),
                        #         filename=item["value"].split("/")[-1],
                        #         content_type="image/jpeg",
                        #     )
                        # 这里暂不支持文件上传，后续考虑添加文件读取节点再来实现
                        pass
                    elif item.Type == VarType.String:
                        form_data.add_field(
                            replace_vars(item.Key, InputArgs),
                            replace_vars(item.Value, InputArgs),
                        )
                    pass
                body = form_data
                # FormData会自动设置content-type，不需要手动设置

            # 如果有content-type，添加到headers中
            if content_type and "Content-Type" not in headers:
                headers["Content-Type"] = content_type

            # 发送HTTP请求
            async with aiohttp.ClientSession(
                cookies=cookies, timeout=timeout
            ) as session:
                async with session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    data=(
                        body
                        if body_config.Type
                        not in [
                            HttpRequestBodyType.JSON,
                            HttpRequestBodyType.XWWWFORMURL,
                        ]
                        else None
                    ),
                    json=body if body_config.Type == HttpRequestBodyType.JSON else None,
                    params=(
                        body
                        if body_config.Type == HttpRequestBodyType.XWWWFORMURL
                        else None
                    ),
                ) as response:
                    # 读取响应内容
                    response_headers = dict(response.headers)
                    response_cookies = dict(response.cookies)
                    response_status = f"{response.status} {response.reason}"
                    response_content_type = response.headers.get("Content-Type", "")

                    # 获取返回格式设置
                    return_format = D_RETURN_FORMAT.Data.value

                    # 根据Content-Type处理响应内容
                    response_text: dict | str = None
                    content_type_lower = (
                        response_content_type.lower() if response_content_type else ""
                    )

                    # 判断是否为文本数据
                    is_text_data = (
                        content_type_lower.startswith("text/")
                        or "application/json" in content_type_lower
                        or "application/xml" in content_type_lower
                        or "application/javascript" in content_type_lower
                        or "application/ld+json" in content_type_lower
                        or "application/x-yaml" in content_type_lower
                        or "application/xhtml+xml" in content_type_lower
                        or "application/rss+xml" in content_type_lower
                        or "application/atom+xml" in content_type_lower
                    )

                    # 判断是否为JSON数据
                    is_json_data = "application/json" in content_type_lower

                    # 强制返回特定格式
                    if return_format == HttpResponseFormat.BINARY:
                        # 强制作为二进制处理
                        binary_data = await response.read()
                        base64_data = base64.b64encode(binary_data).decode("utf-8")
                        response_text = base64_data
                    elif return_format == HttpResponseFormat.JSON:
                        # 强制作为JSON处理
                        try:
                            # 先尝试直接使用response.json()
                            response_text = await response.json(content_type=None)
                        except Exception as json_err:
                            # 如果json()失败，尝试先获取文本再解析
                            try:
                                charset = "utf-8"  # 默认使用 UTF-8
                                if "charset=" in content_type_lower:
                                    charset = (
                                        content_type_lower.split("charset=")[-1]
                                        .split(";")[0]
                                        .strip()
                                    )
                                text_data = await response.text(
                                    encoding=charset, errors="replace"
                                )
                                response_text = json.loads(text_data)
                            except Exception as e:
                                # 如果仍然失败，则报错
                                logger.warning(f"JSON解析失败: {str(e)}，返回原始文本")
                                raise Exception(f"JSON解析失败: {str(e)}")
                    elif return_format == HttpResponseFormat.TEXT:
                        # 强制作为文本处理
                        charset = "utf-8"  # 默认使用 UTF-8
                        if "charset=" in content_type_lower:
                            charset = (
                                content_type_lower.split("charset=")[-1]
                                .split(";")[0]
                                .strip()
                            )
                        response_text = await response.text(
                            encoding=charset, errors="replace"
                        )
                    
                    # 更新结果
                    self.data.Results.ById["DR_STATUS"].Data.value = response_status
                    self.data.Results.ById["DR_HEADER"].Data.value = json.dumps(
                        response_headers, ensure_ascii=False
                    )
                    self.data.Results.ById["DR_COOKIE"].Data.value = json.dumps(
                        response_cookies, ensure_ascii=False
                    )
                    self.data.Results.ById["DR_CONTENTTYPE"].Data.value = (
                        response_content_type
                    )
                    self.data.Results.ById["DR_RESPONSE"].Data.value = response_text

            # 设置所有输出状态为成功
            self.setAllOutputStatus(FARunStatus.Success)
            return []

        except Exception as e:
            error_msg = traceback.format_exc()
            raise Exception(f"HTTP请求执行失败: {error_msg}")

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
        thisnode.add_handle(VFNodeConnectionType.Outputs, "output_status", "STATUS")
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
                Label="返回格式",
                Type="Any",
                Data=HttpResponseFormat.TEXT,
                UiType="@/FlowABuiltin/UI_HTTP_RETURN_FORMAT",
            ),
            payload_id="D_RETURN_FORMAT",
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
            handle_id="output_status",
            result_id="DR_STATUS",
        )
        thisnode.add_result_into_outputs(
            VFNodeContentData(
                Label="返回头",
                Type="String",
                Data="",
            ),
            handle_id="output_res",
            result_id="DR_HEADER",
        )
        thisnode.add_result_into_outputs(
            VFNodeContentData(
                Label="返回Cookie",
                Type="String",
                Data="",
            ),
            handle_id="output_res",
            result_id="DR_COOKIE",
        )
        thisnode.add_result_into_outputs(
            VFNodeContentData(
                Label="返回类型",
                Type="String",
                Data="",
            ),
            handle_id="output_res",
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

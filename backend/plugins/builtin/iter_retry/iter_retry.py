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
from app.utils.vueRef import RefType
from app.schemas.VFNodeClass import VFNode
from app.schemas.vfnode import (
    VFNodeInfo,
    VFEdgeInfo,
    VFNodeData,
    VFlowData,
)
from app.schemas.fanode import FARunStatus
from app.schemas.farequest import (
    ValidationError,
    FANodeUpdateType,
    FANodeUpdateData,
)
from app.schemas.vfnode_contentdata import VarType
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
    VFNodeHandleDataANode,
    FromInnerPath,
    RefItemValue,
)
from app.utils.tools import (
    read_yaml,
    reduceGet,
    getNestedLayout,
    generateNodeId,
    regexMatchOriginalNodeId,
    regexMatchNodeId,
    concatNestedNodeId,
    buildCache4GenerateKey,
    generateCacheKey,
)
from app.utils.db4node import loadNodeConfig, setNodeConfig


if TYPE_CHECKING:
    from app.services.FARunner import FARunner
    from app.services.FAValidator import FAValidator

from ..UI_Components.UI_InputVars import InputVarModel


class RetryType(StrEnum):
    Immediate = "Immediate"
    Delay = "Delay"
    Exponential = "Exponential"


class RetrySettingModel(BaseModel):
    Type: RetryType = RetryType.Immediate
    Num: int = 5
    Delay: float = 5.0
    ExpBase: float = 2.0
    ExpFactor: float = 1.5
    pass


async def init_node_class():
    pass


class IterRetry(FATaskNode):
    def __init__(self, wid: str, nodeinfo: VFNodeInfo, runner: "FARunner"):
        super().__init__(wid, nodeinfo, runner)

        self.cacheKey4Child = None
        self.cacheKey4Input = None
        self.cacheKey4Ouput = None
        self.cacheKey4Next = None
        self.cacheKey4PostNode = None
        pass

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
            D_ITER_ARRAY: VFNodeContentData = node_payloads.ById["D_ITER_ARRAY"]
            if D_ITER_ARRAY.Data.value not in selfVars:
                error_msgs.append(
                    f"【迭代数组】没有该变量选项{D_ITER_ARRAY.Data.value}"
                )

            aoutputVars = await validator.getConnectionByPath(
                self.id,
                [
                    CONNECT_DATA_TO_SELECT,
                    VFNodeConnectionType.Self,
                    "attach_output",
                ],
            )
            node_results = self.data.Results
            for rid in node_results.Order:
                ref_data = node_results.ById[rid].Config.Ref
                if (
                    ref_data is None
                    or not isinstance(ref_data, str)
                    or len(ref_data) <= 0
                ):
                    error_msgs.append(f"结果{rid}没有配置输出选项")
                else:
                    if ref_data not in aoutputVars:
                        error_msgs.append(f"没有该输出选项{ref_data}")
                pass

        except Exception as e:
            errmsg = traceback.format_exc()
            error_msgs.append(f"获取内容失败{str(errmsg)}")

        if len(error_msgs) > 0:
            return ValidationError(nid=self.id, errors=error_msgs)
        return None

    async def run(self) -> List[FANodeUpdateData]:
        pass

    async def getContentByPath(
        self, request_nid: str, path: FromInnerPath
    ) -> VFNodeContentData:
        req_layout = getNestedLayout(request_nid)
        self_layout = getNestedLayout(self.id)
        assert len(req_layout) >= len(self_layout), "子节点应该比父节点更深"
        node_payloads = self.data.Payloads
        if path.ContentId == "D_ITER_INDEX":
            D_ITER_INDEX: VFNodeContentData = node_payloads.ById["D_ITER_INDEX"]
            return VFNodeContentData(
                Label=D_ITER_INDEX.Label,
                Type=D_ITER_INDEX.Type,
                Data=RefType(req_layout[len(self_layout)]),
            )
        elif path.ContentId == "D_ITER_ITEM":
            D_ITER_ARRAY: VFNodeContentData = node_payloads.ById["D_ITER_ARRAY"]
            return VFNodeContentData(
                Label=D_ITER_ARRAY.Label,
                Type=D_ITER_ARRAY.Type,
                Data=RefType(self.iter_array[req_layout[len(self_layout)]]),
            )
        return self.data.getContent(path.ContentName).ById[path.ContentId]

    def getCacheKey(self, request_nid: str):
        """
        对于自身，返回None以跳过缓存
        对于内部节点 返回带payload，不用result
        对于后继节点，返回带payload和result，以及output的缓存
        """
        if request_nid == self.id:
            return None
        nest_layout = getNestedLayout(self.id)
        re_nid, _ = regexMatchNodeId(self.data.Nesting.ANodes["next"].Nid)
        next_anode_ids = [
            concatNestedNodeId(re_nid, nest_layout + [iter_idx])
            for iter_idx in range(self.iter_array_len)
        ]
        re_nid, _ = regexMatchNodeId(self.data.Nesting.ANodes["output"].Nid)
        output_anode_id = concatNestedNodeId(re_nid, nest_layout)

        req_node = self.runner().getNode(request_nid)
        if req_node.parentNode == self.id:
            if self.cacheKey4Child is None:
                if data := buildCache4GenerateKey(
                    self,
                    cache_parentNode=True,
                    cache_preNodes=True,
                    cache_Connections=True,
                    cache_Payloads=True,
                    cache_Results=False,
                    cache_Config=True,
                    cache_Attaching=True,
                    cache_Nesting=True,
                ):
                    self.cacheKey4Child = generateCacheKey(data)
            return self.cacheKey4Child
        else:
            if self.cacheKey4PostNode is None:
                outanode = self.runner().getNode(output_anode_id)

                nextanodes = [
                    self.runner().getNode(next_anode_id)
                    for next_anode_id in next_anode_ids
                ]
                if outanode and all(nextanodes):
                    if data := buildCache4GenerateKey(
                        self,
                        cache_parentNode=True,
                        cache_preNodes=True,
                        cache_Connections=True,
                        cache_Payloads=True,
                        cache_Results=True,
                        cache_Config=True,
                        cache_Attaching=True,
                        cache_Nesting=True,
                        other={
                            "outnode": buildCache4GenerateKey(
                                outanode,
                                cache_parentNode=False,
                                cache_preNodes=True,
                                cache_Connections=True,
                                cache_Payloads=True,
                                cache_Results=True,
                                cache_Config=True,
                                cache_Attaching=True,
                                cache_Nesting=True,
                            ),
                            "nextnode": [
                                buildCache4GenerateKey(
                                    nextnode,
                                    cache_parentNode=False,
                                    cache_preNodes=True,
                                    cache_Connections=True,
                                    cache_Payloads=True,
                                    cache_Results=True,
                                    cache_Config=True,
                                    cache_Attaching=True,
                                    cache_Nesting=True,
                                )
                                for nextnode in nextanodes
                            ],
                        },
                    ):
                        self.cacheKey4PostNode = generateCacheKey(data)
                    pass
            return self.cacheKey4PostNode
        pass

    @staticmethod
    def getNodeCreateInfo():
        thisnode = VFNode("basenode")
        thisnode.set_flag(VFNodeFlag.IsTask | VFNodeFlag.IsNested)
        thisnode.init_as_nested_node("ITERRETRY")
        thisnode.set_size(200, 200)

        thisnode.add_handle(VFNodeConnectionType.Inputs, "input", "Input")
        thisnode.add_handle(VFNodeConnectionType.Outputs, "output", "Output")
        thisnode.add_handle(VFNodeConnectionType.Self, "self")
        thisnode.add_handle(VFNodeConnectionType.Self, "attach_output")
        thisnode.add_handle(VFNodeConnectionType.Attach, "Attach")

        thisnode.add_attached_node("input", "@/FlowABuiltin/attach_node_input")
        thisnode.add_attached_node("output", "@/FlowABuiltin/attach_node_output")
        thisnode.add_attached_node("break", "@/FlowABuiltin/attach_node_break")

        thisnode.add_handle_data(
            VFNodeConnectionType.Self,
            "self",
            VFNodeHandleData(
                Type=VFNodeConnectionDataType.FromOuter,
                HandleId="input",
            ),
        )
        thisnode.add_handle_data(
            VFNodeConnectionType.Self,
            "attach_output",
            VFNodeHandleData(
                Type=VFNodeConnectionDataType.FromAttached,
                ANode={
                    "output": VFNodeHandleDataANode(
                        ConnectionType=VFNodeConnectionType.Self,
                        HandleId="self",
                    )
                },
            ),
        )

        # 只用于UI展示，没有实际作用
        thisnode.add_payload(
            VFNodeContentData(
                Label="",
                Type="List",
                Data=None,
                UiType="@/FlowABuiltin/UI_ITER_RUN_INNER_VAR",
            ),
        )

        # 这两个，删掉UiType就不会出现在UI上了，全部由上边的来展示
        pid_D_ITER_ITEM = thisnode.add_payload(
            VFNodeContentData(
                Label="迭代项目",
                Type="Any",
                Data=None,
            ),
            payload_id="D_ITER_ITEM",
        )
        pid_D_ITER_INDEX = thisnode.add_payload(
            VFNodeContentData(
                Label="重试次数",
                Type="Integer",
                Data=None,
            ),
            payload_id="D_ITER_INDEX",
        )
        thisnode.add_handle_data(
            VFNodeConnectionType.Attach,
            "Attach",
            VFNodeHandleData(
                Type=VFNodeConnectionDataType.FromInner,
                Path=FromInnerPath(ContentName="Payloads", ContentId=pid_D_ITER_ITEM),
            ),
        )
        thisnode.add_handle_data(
            VFNodeConnectionType.Attach,
            "Attach",
            VFNodeHandleData(
                Type=VFNodeConnectionDataType.FromInner,
                Path=FromInnerPath(ContentName="Payloads", ContentId=pid_D_ITER_INDEX),
            ),
        )

        thisnode.add_payload(
            VFNodeContentData(
                Label="重试设置",
                Type="Dict",
                Data=RetrySettingModel(),
                UiType="@/FlowABuiltin/UI_ITER_RETRY_SETTING",
            ),
            payload_id="D_ITER_RETRY_SETTING",
        )

        # 只用于UI展示，没有实际作用
        thisnode.add_payload(
            VFNodeContentData(
                Label="",
                Type="List",
                Data=None,
                UiType="@/FlowABuiltin/UI_ITER_RETRY_INOUT",
            ),
        )

        # 这两个，删掉UiType就不会出现在UI上了，全部由上边的来展示
        thisnode.add_payload(
            VFNodeContentData(
                Label="初始变量",
                Type="Ref",
                Data="",
            ),
            payload_id="D_IN_NODE",
        )
        thisnode.add_payload(
            VFNodeContentData(
                Label="迭代变量",
                Type="Ref",
                Data="",
            ),
            payload_id="D_OUT_NODE",
        )

        thisnode.add_handle_data(
            VFNodeConnectionType.Attach,
            "Attach",
            VFNodeHandleData(
                Type=VFNodeConnectionDataType.FromOuter,
                HandleId="input",
            ),
        )
        thisnode.add_result_into_outputs(
            VFNodeContentData(
                Label="输出变量",
                Type="Any",
                Data=None,
            ),
            handle_id="output",
            result_id="D_FINAL_OUTPUT",
        )
        thisnode.set_outputs_ui_type("@/FlowABuiltin/UI_TAG_OUTPUTS")
        return thisnode


# 必须存在
EXPORT_NODE = IterRetry
# 可选存在
EXPORT_INIT = init_node_class

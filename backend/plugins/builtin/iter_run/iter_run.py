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
from app.schemas.VFlowData import (
    VFNodeInfo,
    VFEdgeInfo,
    VFlowData,
)
from app.schemas.VFlowRunData import (
    FARunStatus,
    VFNodeCacheKey,
    VFNodeCacheKeyBefore,
    VFNodeCacheKeyAfter,
)
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
)
from app.utils.cacheKey import buildCache4GenerateKey
from app.services.FARunner import FARunner
from app.services.FAValidator import FAValidator


async def init_node_class():
    pass


class IterRun(FATaskNode):
    def __init__(self, wid: str, nodeinfo: VFNodeInfo, runner: "FARunner"):
        super().__init__(wid, nodeinfo, runner)

        self.cacheKey4Child = None
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
        from app.nodes import FANODE_REGISTRY

        nest_layout = getNestedLayout(self.id)
        node_payloads = self.data.Payloads
        node_results = self.data.Results

        # 获取迭代数组 ===============================================
        D_ITER_ARRAY: VFNodeContentData = node_payloads.ById["D_ITER_ARRAY"]
        D_ITER_INDEX: VFNodeContentData = node_payloads.ById["D_ITER_INDEX"]
        self.iter_array = await self.runner().getRefData(
            self.id, D_ITER_ARRAY.Data.value
        )
        self.iter_array_len = len(self.iter_array)

        # 构建子图 ================================================
        flowdata: VFlowData = self.runner().flowdata
        child_node_infos: Dict[str, VFNodeInfo] = {}
        child_edge_infos: Dict[str, VFEdgeInfo] = {}
        # 收集所有子节点
        for nodeinfo in flowdata.nodes:
            if nodeinfo.parentNode == self.oriid and (
                VFNodeFlag.IsTask & nodeinfo.data.Flag
                or VFNodeFlag.IsAttached & nodeinfo.data.Flag
            ):
                child_node_infos[nodeinfo.id] = nodeinfo
            pass
        pass
        for edgeinfo in flowdata.edges:
            if (
                edgeinfo.source in child_node_infos
                and edgeinfo.target in child_node_infos
            ):
                child_edge_infos[edgeinfo.id] = edgeinfo
            pass
        pass

        # 收集附属节点
        input_anode_info = None
        output_anode_info = None
        next_anode_info = None
        for nodeinfo in flowdata.nodes:
            if nodeinfo.id == self.data.Nesting.ANodes["input"].Nid:
                input_anode_info = nodeinfo
            elif nodeinfo.id == self.data.Nesting.ANodes["output"].Nid:
                output_anode_info = nodeinfo
            elif nodeinfo.id == self.data.Nesting.ANodes["next"].Nid:
                next_anode_info = nodeinfo
            pass
        assert (
            input_anode_info is not None
            and output_anode_info is not None
            and next_anode_info is not None
        )
        pass
        input_anode: FATaskNode = FANODE_REGISTRY[input_anode_info.data.NType](
            self.wid,
            input_anode_info,
            self.runner(),
        )
        output_anode: FATaskNode = FANODE_REGISTRY[input_anode_info.data.NType](
            self.wid,
            output_anode_info,
            self.runner(),
        )
        for node in [input_anode, output_anode]:
            re_nid, _ = regexMatchNodeId(node.id)
            new_nid = concatNestedNodeId(re_nid, nest_layout)
            node.setNodeID(new_nid)
            self.runner().addNode(node.id, node)
        asyncio.create_task(self.runner().getNode(input_anode.id).invoke())
        logger.info(f"启动附属节点{input_anode.data.Label} {node.id}")
        pass
        # 开始迭代
        for iter_idx in range(self.iter_array_len):
            # 构建next附属节点
            next_anode: FATaskNode = (FANODE_REGISTRY[next_anode_info.data.NType])(
                self.wid,
                next_anode_info,
                self.runner(),
            )
            re_nid, _ = regexMatchNodeId(next_anode.id)
            new_nid = concatNestedNodeId(re_nid, nest_layout + [iter_idx])
            next_anode.setNodeID(new_nid)
            self.runner().addNode(next_anode.id, next_anode)
            pass

            # 根据结果数组搜寻目标输出节点
            node_results_dict = {}
            for rid in node_results.Order:
                item: VFNodeContentData = node_results.ById[rid]
                item_ref = RefItemValue.model_validate_json(item.Config.Ref)
                nid_layout = getNestedLayout(item_ref.nid)
                assert len(nest_layout) == len(nid_layout) - 1, "迭代节点嵌套层数不匹配"
                re_nid, _ = regexMatchNodeId(item_ref.nid)
                item_nid_pattern = concatNestedNodeId(re_nid, nest_layout)
                item_nid_pattern = regexMatchOriginalNodeId(item_nid_pattern)
                node_results_dict[rid] = {
                    "item_nid_pattern": item_nid_pattern,
                    "contentpath": item_ref.path,
                }
            # 构建其余子节点
            anode_ids = set([input_anode.oriid, output_anode.oriid, next_anode.oriid])
            child_nodes: Dict[str, FATaskNode] = {}
            for child_id, child_info in child_node_infos.items():
                if child_info.id in anode_ids:
                    continue
                child_node: FATaskNode = (FANODE_REGISTRY[child_info.data.NType])(
                    self.wid,
                    child_info,
                    self.runner(),
                )
                re_nid, _ = regexMatchNodeId(child_node.id)
                new_nid = concatNestedNodeId(re_nid, nest_layout + [iter_idx])
                child_node.setNodeID(new_nid)
                self.runner().addNode(new_nid, child_node)
                child_nodes[child_node.id] = child_node
                pass
                # 真正将结果加入数组
                for rid in node_results_dict.keys():
                    nid_pattern = node_results_dict[rid]["item_nid_pattern"]
                    if nid_pattern in child_node.id:
                        contentpath: FromInnerPath = node_results_dict[rid][
                            "contentpath"
                        ]
                        node_results.ById[rid].Data.value.append(
                            (
                                await child_node.getContentByPath(self.id, contentpath)
                            ).Data
                        )
                pass
            # 构建节点连接关系
            for edgeinfo in child_edge_infos.values():
                src_node_info = child_node_infos[edgeinfo.source]
                tgt_node_info = child_node_infos[edgeinfo.target]
                if src_node_info.id == input_anode.oriid:
                    src_node = input_anode
                    pass
                else:
                    re_nid, _ = regexMatchNodeId(edgeinfo.source)
                    src_nid = concatNestedNodeId(re_nid, nest_layout + [iter_idx])
                    src_node = self.runner().getNode(src_nid)
                if tgt_node_info.id == output_anode.oriid:
                    tgt_node = output_anode
                    pass
                elif tgt_node_info.id == next_anode.oriid:
                    tgt_node = next_anode
                    pass
                else:
                    re_nid, _ = regexMatchNodeId(edgeinfo.target)
                    tgt_nid = concatNestedNodeId(re_nid, nest_layout + [iter_idx])
                    tgt_node = self.runner().getNode(tgt_nid)
                    pass

                source_handle = edgeinfo.sourceHandle
                target_handle = edgeinfo.targetHandle
                tgt_node.addPreNode(src_node, source_handle)
            pass
            # 启动子节点
            for nid in child_nodes.keys():
                asyncio.create_task(child_nodes[nid].invoke())
            # 启动next附属节点
            task_next = asyncio.create_task(next_anode.invoke())
            await task_next
            pass
        task_output = asyncio.create_task(output_anode.invoke())
        await task_output
        if output_anode.runStatus == FARunStatus.Success:
            self.setAllOutputStatus(FARunStatus.Success)
            return []
        elif output_anode.runStatus == FARunStatus.Canceled:
            self.setAllOutputStatus(FARunStatus.Canceled)
            return []
        else:
            raise Exception(f"内部节点存在运行错误，迭代节点执行失败")

    async def getContentByPath(
        self, request_nid: str, path: FromInnerPath
    ) -> VFNodeContentData:
        req_layout = getNestedLayout(request_nid)
        self_layout = getNestedLayout(self.id)
        assert len(req_layout) >= len(self_layout), "子节点应该比父节点更深"
        node_payloads = self.data.Payloads
        if path.ContentName == "Payloads" and path.ContentId == "D_ITER_INDEX":
            D_ITER_INDEX: VFNodeContentData = node_payloads.ById["D_ITER_INDEX"]
            return VFNodeContentData(
                Label=D_ITER_INDEX.Label,
                Type=D_ITER_INDEX.Type,
                Data=RefType(req_layout[len(self_layout)]),
            )
        elif path.ContentName == "Payloads" and path.ContentId == "D_ITER_ITEM":
            D_ITER_ARRAY: VFNodeContentData = node_payloads.ById["D_ITER_ARRAY"]
            return VFNodeContentData(
                Label=D_ITER_ARRAY.Label,
                Type=D_ITER_ARRAY.Type,
                Data=RefType(self.iter_array[req_layout[len(self_layout)]]),
            )
        return self.data.getContent(path.ContentName).ById[path.ContentId]

    def getCacheKey(self, request_nid: str):
        """
        对于自身，跳过缓存
        对于内部节点 返回带payload，不用result
        对于后继节点，返回带payload和result，以及output的缓存
        """
        if request_nid == self.id:
            return VFNodeCacheKey(
                Before=VFNodeCacheKeyBefore.Skip,
                After=VFNodeCacheKeyAfter.Skip,
            )
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
                self.cacheKey4Child = buildCache4GenerateKey(
                    self,
                    cache_parentNode=True,
                    cache_preNodes=True,
                    cache_Connections=True,
                    cache_Payloads=True,
                    cache_Results=False,
                    cache_Config=True,
                    cache_Attaching=True,
                    cache_Nesting=True,
                )
            return self.cacheKey4Child
        else:
            if self.cacheKey4PostNode is None:
                outanode = self.runner().getNode(output_anode_id)

                nextanodes = [
                    self.runner().getNode(next_anode_id)
                    for next_anode_id in next_anode_ids
                ]
                if outanode and all(nextanodes):
                    self.cacheKey4PostNode = buildCache4GenerateKey(
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
                            ).model_dump(),
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
                                ).model_dump()
                                for nextnode in nextanodes
                            ],
                        },
                    )
                    pass
            return self.cacheKey4PostNode
        pass

    @staticmethod
    def getNodeCreateInfo():
        thisnode = VFNode("basenode")
        thisnode.set_flag(VFNodeFlag.IsTask | VFNodeFlag.IsNested)
        thisnode.init_as_nested_node("ITERRUN")
        thisnode.set_size(200, 200)

        thisnode.add_handle(VFNodeConnectionType.Inputs, "input", "Input")
        thisnode.add_handle(VFNodeConnectionType.Outputs, "output", "Output")
        thisnode.add_handle(VFNodeConnectionType.Self, "self")
        thisnode.add_handle(VFNodeConnectionType.Self, "attach_output")
        thisnode.add_handle(VFNodeConnectionType.Attach, "Attach")

        thisnode.add_attached_node("input", "@/FlowABuiltin/attach_node_input")
        thisnode.add_attached_node("output", "@/FlowABuiltin/attach_node_output")
        thisnode.add_attached_node("next", "@/FlowABuiltin/attach_node_next")

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
                Label="迭代索引",
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
                Label="迭代数组",
                Type="String",
                Data="",
                UiType="@/FlowABuiltin/UI_ITER_RUN_ITER_ARRAY",
            ),
            payload_id="D_ITER_ARRAY",
        )

        thisnode.add_handle_data(
            VFNodeConnectionType.Attach,
            "Attach",
            VFNodeHandleData(
                Type=VFNodeConnectionDataType.FromOuter,
                HandleId="input",
            ),
        )

        thisnode.set_outputs_ui_type("@/FlowABuiltin/UI_ITER_RUN_OUTPUT")
        return thisnode


# 必须存在
EXPORT_NODE = IterRun
# 可选存在
EXPORT_INIT = init_node_class

from typing import List, Dict, Optional, TYPE_CHECKING, Any, Union, Literal
import asyncio
import traceback
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
from app.utils.db4node import loadNodeConfig, setNodeConfig
from app.services.CacheMgr import buildCache4GenerateKey


if TYPE_CHECKING:
    from app.services.FARunner import FARunner
    from app.services.FAValidator import FAValidator


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
            D_IN_NODE: VFNodeContentData = node_payloads.ById["D_IN_NODE"]
            if D_IN_NODE.Data.value not in selfVars:
                error_msgs.append(f"【初始变量】没有该变量选项{D_IN_NODE.Data.value}")

            aoutputVars = await validator.getConnectionByPath(
                self.id,
                [
                    CONNECT_DATA_TO_SELECT,
                    VFNodeConnectionType.Self,
                    "attach_output",
                ],
            )
            D_OUT_NODE: VFNodeContentData = node_payloads.ById["D_OUT_NODE"]
            if D_OUT_NODE.Data.value not in aoutputVars:
                error_msgs.append(f"【迭代变量】没有该变量选项{D_OUT_NODE.Data.value}")
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

        # 获取迭代项目 ===============================================
        D_FINAL_OUTPUT: VFNodeContentData = node_results.ById["D_FINAL_OUTPUT"]
        D_IN_NODE: VFNodeContentData = node_payloads.ById["D_IN_NODE"]
        D_OUT_NODE: VFNodeContentData = node_payloads.ById["D_OUT_NODE"]
        D_ITER_RETRY_SETTING: VFNodeContentData = node_payloads.ById[
            "D_ITER_RETRY_SETTING"
        ]
        retry_config = RetrySettingModel.model_validate(D_ITER_RETRY_SETTING.Data.value)

        self.retry_item = await self.runner().getRefData(self.id, D_IN_NODE.Data.value)
        self.retry_index = 0

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
        break_anode_info = None
        for nodeinfo in flowdata.nodes:
            if nodeinfo.id == self.data.Nesting.ANodes["input"].Nid:
                input_anode_info = nodeinfo
            elif nodeinfo.id == self.data.Nesting.ANodes["output"].Nid:
                output_anode_info = nodeinfo
            elif nodeinfo.id == self.data.Nesting.ANodes["break"].Nid:
                break_anode_info = nodeinfo
            pass
        assert (
            input_anode_info is not None
            and output_anode_info is not None
            and break_anode_info is not None
        )
        pass
        input_anode: FATaskNode = FANODE_REGISTRY[input_anode_info.data.NType](
            self.wid,
            input_anode_info,
            self.runner(),
        )
        re_nid, _ = regexMatchNodeId(input_anode.id)
        new_nid = concatNestedNodeId(re_nid, nest_layout)
        input_anode.setNodeID(new_nid)
        self.runner().addNode(input_anode.id, input_anode)
        asyncio.create_task(self.runner().getNode(input_anode.id).invoke())
        logger.info(f"启动附属节点{input_anode.data.Label} {input_anode.id}")
        pass
        # 开始迭代
        AddInNodes: List[str] = []
        for retry_idx in range(retry_config.Num):
            self.retry_index = retry_idx
            # 构建break附属节点
            break_anode: FATaskNode = (FANODE_REGISTRY[break_anode_info.data.NType])(
                self.wid,
                break_anode_info,
                self.runner(),
            )
            output_anode: FATaskNode = FANODE_REGISTRY[input_anode_info.data.NType](
                self.wid,
                output_anode_info,
                self.runner(),
            )
            for node in [break_anode, output_anode]:
                re_nid, _ = regexMatchNodeId(node.id)
                new_nid = concatNestedNodeId(re_nid, nest_layout)
                node.setNodeID(new_nid)
                AddInNodes.append(new_nid)
                self.runner().addNode(node.id, node)
            pass

            # 构建其余子节点
            anode_ids = set([input_anode.oriid, output_anode.oriid, break_anode.oriid])
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
                new_nid = concatNestedNodeId(re_nid, nest_layout)
                child_node.setNodeID(new_nid)
                AddInNodes.append(new_nid)
                self.runner().addNode(new_nid, child_node)
                child_nodes[child_node.id] = child_node
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
                    src_nid = concatNestedNodeId(re_nid, nest_layout)
                    src_node = self.runner().getNode(src_nid)
                if tgt_node_info.id == output_anode.oriid:
                    tgt_node = output_anode
                    pass
                elif tgt_node_info.id == break_anode.oriid:
                    tgt_node = break_anode
                    pass
                else:
                    re_nid, _ = regexMatchNodeId(edgeinfo.target)
                    tgt_nid = concatNestedNodeId(re_nid, nest_layout)
                    tgt_node = self.runner().getNode(tgt_nid)
                    pass

                source_handle = edgeinfo.sourceHandle
                target_handle = edgeinfo.targetHandle
                tgt_node.addPreNode(src_node, source_handle)
            pass
            # 启动子节点
            for nid in child_nodes.keys():
                asyncio.create_task(child_nodes[nid].invoke())
            # 启动output/next附属节点
            task_output = asyncio.create_task(output_anode.invoke())
            task_break = asyncio.create_task(break_anode.invoke())
            await asyncio.wait([task_output, task_break])
            pass
            if break_anode.runStatus == FARunStatus.Success:
                self.setAllOutputStatus(FARunStatus.Success)
                D_FINAL_OUTPUT.Data.value = self.retry_item
                return []
            if output_anode.runStatus == FARunStatus.Success:
                self.retry_item = await self.runner().getRefData(
                    self.id, D_OUT_NODE.Data.value
                )

            logger.error(f"不满足条件，继续重试{retry_idx+1}/{retry_config.Num}")
            for nid in AddInNodes:
                self.runner().rmNode(nid)
            AddInNodes.clear()
            continue
        pass
        raise Exception(f"子节点全部运行失败，共迭代重试{retry_config.Num}次")

    async def getContentByPath(
        self, request_nid: str, path: FromInnerPath
    ) -> VFNodeContentData:
        node_payloads = self.data.Payloads
        if path.ContentName == "Payloads" and path.ContentId == "D_ITER_INDEX":
            D_ITER_INDEX: VFNodeContentData = node_payloads.ById["D_ITER_INDEX"]
            return VFNodeContentData(
                Label=D_ITER_INDEX.Label,
                Type=D_ITER_INDEX.Type,
                Data=RefType(self.retry_index),
            )
        elif path.ContentName == "Payloads" and path.ContentId == "D_ITER_ITEM":
            D_ITER_ITEM: VFNodeContentData = node_payloads.ById["D_ITER_ITEM"]
            return VFNodeContentData(
                Label=D_ITER_ITEM.Label,
                Type=D_ITER_ITEM.Type,
                Data=RefType(self.retry_item),
            )
        return self.data.getContent(path.ContentName).ById[path.ContentId]

    def getCacheKey(self, request_nid: str) -> VFNodeCacheKey:
        """
        重试节点相当于一个节点组，因此不应该重新执行流程，直接获取缓存输出就行了
        对于自身和后继节点，返回带payload和result，以及output的缓存
        对于内部节点 返回None
        """

        req_node = self.runner().getNode(request_nid)
        if req_node.parentNode == self.id:
            # 如果重试节点需要执行，则内部节点也需要重新执行并且不能保存缓存
            # 并且内部节点不能保存缓存，因为每次输入数据都不一样
            return VFNodeCacheKey(
                Before=VFNodeCacheKeyBefore.Skip,
                After=VFNodeCacheKeyAfter.Skip,
            )
        else:
            # 对于外部节点，包括他自己，则作为一个节点就可以了
            if self.cacheKey4PostNode is None:
                subgraph = self.runner().getSubGraph(self.id)
                self.cacheKey4PostNode = buildCache4GenerateKey(
                    self,
                    cache_parentNode=True,
                    cache_preNodes=True,
                    cache_Connections=True,
                    cache_Payloads=True,
                    cache_Results=False,
                    cache_Config=True,
                    cache_Attaching=True,
                    cache_Nesting=True,
                    other={"subgraph": subgraph.model_dump()},
                )
                pass
            return self.cacheKey4PostNode
        pass

    @staticmethod
    def getNodeCreateInfo():
        thisnode = VFNode("basenode")
        thisnode.set_flag(VFNodeFlag.IsTask | VFNodeFlag.IsNested)
        thisnode.init_as_nested_node(None)
        thisnode.set_size(200, 200)

        thisnode.add_handle(VFNodeConnectionType.Inputs, "input", "Input")
        thisnode.add_handle(VFNodeConnectionType.Outputs, "output", "OUTPUT")
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
                UiType="@/FlowABuiltin/UI_ITER_RETRY_INNER_VAR",
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

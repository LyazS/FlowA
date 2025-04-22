from typing import Dict, List, TYPE_CHECKING, Set, Union
import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo
from loguru import logger
from app.schemas.VFlowData import VFlowData, VFNodeInfo, VFEdgeInfo
from app.schemas.VFlowRunData import FARunStatus
from app.services.messageMgr import ALL_MESSAGES_MGR
from app.services.CacheMgr import CacheMgr
from app.schemas.farequest import (
    ValidationError,
    FANodeUpdateType,
    FANodeUpdateData,
    SSEResponse,
    SSEResponseData,
    SSEResponseType,
    FAWorkflow,
)
from app.utils.tools import (
    getNestedLayout,
    regexMatchOriginalNodeId,
    regexMatchNodeId,
    concatNestedNodeId,
)
from app.utils.vueRef import serialize_ref
from app.schemas.VFNodeInterface import (
    VFNodeFlag,
    FromInnerPath,
    VFNodeContentData,
)
from app.uisdk import RefVarItem

if TYPE_CHECKING:
    from app.nodes import FABaseNode


class FARunner:
    def __init__(self, wid: str, vflowdata: dict):
        self.wid = wid
        self.oriflowdata = vflowdata
        self.flowdata: VFlowData = VFlowData.model_validate(vflowdata)
        self.nodes: Dict[str, "FABaseNode"] = {}
        self.status: FARunStatus = FARunStatus.Pending
        # 时间戳
        self.starttime = None
        self.endtime = None

        self.cancel_event = asyncio.Event()
        self.running_tasks: Set[asyncio.Task] = set()  # 跟踪所有节点任务
        self.cachemgr = CacheMgr(self.wid)

        # 方便的全局父子节点结构
        self.nestedGraph: Dict[str, List[str]] = {}

        # 预先建立节点和边的索引结构，提高查询效率
        self.node_map: Dict[str, VFNodeInfo] = {
            node.id: node for node in self.flowdata.nodes
        }
        self.source_edges: Dict[str, List[VFEdgeInfo]] = {}
        self.target_edges: Dict[str, List[VFEdgeInfo]] = {}

        # 初始化索引结构
        self.buildNestedGraph()
        self.buildEdgeIndex()

    def buildNestedGraph(self):
        for nodeinfo in self.flowdata.nodes:
            if nodeinfo.parentNode:
                if nodeinfo.parentNode not in self.nestedGraph:
                    self.nestedGraph[nodeinfo.parentNode] = []
                self.nestedGraph[nodeinfo.parentNode].append(nodeinfo.id)

    def buildEdgeIndex(self):
        """构建边的索引结构，提高查询效率"""
        for edge in self.flowdata.edges:
            # 建立源节点到边的映射
            if edge.source not in self.source_edges:
                self.source_edges[edge.source] = []
            self.source_edges[edge.source].append(edge)

            # 建立目标节点到边的映射
            if edge.target not in self.target_edges:
                self.target_edges[edge.target] = []
            self.target_edges[edge.target].append(edge)

    def getChildrenFromGraph(self, parentid: str):
        return self.nestedGraph.get(parentid, [])

    def getSubGraph(self, parentid: str):
        """
        获取VFlowData结构的子图
        优化版本：使用预先建立的索引结构，避免重复线性搜索
        """
        child_node_infos: Dict[str, VFNodeInfo] = {}
        child_edge_infos: Dict[str, VFEdgeInfo] = {}

        # 使用迭代方式代替递归，避免潜在的栈溢出问题
        queue = [parentid]
        visited = set()

        while queue:
            current_id = queue.pop(0)
            if current_id in visited:
                continue

            visited.add(current_id)
            children = self.getChildrenFromGraph(current_id)

            for child_id in children:
                # 使用预先建立的节点映射，O(1)时间复杂度
                if child_id in self.node_map and child_id not in child_node_infos:
                    child_node = self.node_map[child_id]
                    child_node_infos[child_id] = child_node
                    queue.append(child_id)

        # 使用预先建立的边索引结构收集相关的边
        # 只需要检查子图中的节点作为源节点的边
        for node_id in child_node_infos:
            # 如果该节点作为源节点有边
            if node_id in self.source_edges:
                for edge in self.source_edges[node_id]:
                    # 如果目标节点也在子图中
                    if edge.target in child_node_infos:
                        child_edge_infos[edge.id] = edge

        return VFlowData(
            nodes=list(child_node_infos.values()),
            edges=list(child_edge_infos.values()),
        )

    def addNode(self, nid, node: "FABaseNode"):
        self.nodes[nid] = node

    def rmNode(self, nid):
        if nid in self.nodes:
            del self.nodes[nid]

    def getNode(self, request_nid: str) -> Union["FABaseNode", None]:
        return self.nodes.get(request_nid, None)

    async def getCache(self, request_nid: str, cache_key: str):
        return await self.cachemgr.get(request_nid, cache_key)

    async def setCache(
        self,
        request_nid: str,
        cache_key: str,
        value,
        isCommit: bool = False,
    ):
        await self.cachemgr.set(request_nid, cache_key, value, isCommit)

    async def getRefData(self, request_nid: str, refvalue: str):
        """
        根据curnid获取相对应层级的refdata数据
        针对Ref数据会自动解包，返回原始数据
        """
        # 获取cur节点的层级 =======================================
        cur_level = getNestedLayout(request_nid)
        # 获取ref节点的层级 =======================================
        refdata = RefVarItem.model_validate_json(refvalue)
        ref_level = getNestedLayout(refdata.Nid)

        assert len(ref_level) <= len(cur_level), "层级不匹配"
        for i in range(len(ref_level)):
            ref_level[i] = cur_level[i]
        re_nid, _ = regexMatchNodeId(refdata.Nid)
        ref_replace_nid = concatNestedNodeId(re_nid, ref_level)
        ref_node = self.getNode(ref_replace_nid)
        ref_data: VFNodeContentData = await ref_node.getContentByPath(
            request_nid,
            refdata.Path,
        )
        return serialize_ref(ref_data.Data.value)

    def buildNodes(self):
        from app.nodes import FANODE_REGISTRY

        # 初始化顶层节点
        for nodeinfo in self.flowdata.nodes:
            if nodeinfo.parentNode == None:
                self.addNode(
                    nodeinfo.id,
                    (FANODE_REGISTRY[nodeinfo.data.NType])(
                        self.wid,
                        nodeinfo,
                        self,
                    ),
                )
            pass
        # 构建节点连接关系
        for edgeinfo in self.flowdata.edges:
            if edgeinfo.source in self.nodes and edgeinfo.target in self.nodes:
                if (
                    self.getNode(edgeinfo.source).parentNode != None
                    or self.getNode(edgeinfo.target).parentNode != None
                ):
                    continue
                if not (
                    (VFNodeFlag.IsTask & self.getNode(edgeinfo.source).data.Flag)
                    and (VFNodeFlag.IsTask & self.getNode(edgeinfo.target).data.Flag)
                ):
                    continue
                source_handle = edgeinfo.sourceHandle
                target_handle = edgeinfo.targetHandle
                self.getNode(edgeinfo.target).addPreNode(
                    self.getNode(edgeinfo.source), source_handle
                )
        pass

    async def run(self):
        try:
            self.starttime = datetime.now(ZoneInfo("Asia/Shanghai"))
            logger.info(f"workflow {self.wid} run start")
            self.buildNodes()
            # 启动所有顶层节点
            self.running_tasks = {
                asyncio.create_task(node.invoke()) for node in self.nodes.values()
            }
            self.status = FARunStatus.Running
            await asyncio.gather(*self.running_tasks)
            await self.cachemgr.batchcommit()
            self.endtime = datetime.now(ZoneInfo("Asia/Shanghai"))
            logger.info(f"workflow {self.wid} run success")
            self.status = FARunStatus.Success
            ALL_MESSAGES_MGR.put(
                self.wid,
                SSEResponse(
                    event=SSEResponseType.flowfinish,
                    data=None,
                ),
            )
        except asyncio.CancelledError:
            logger.debug(f"workflow {self.wid} canceled")
            await self.stop()
            self.status = FARunStatus.Canceled
        finally:
            pass

    async def stop(self):
        self.cancel_event.set()
        # 取消所有关联任务
        tasks = list(self.running_tasks)
        self.running_tasks.clear()
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

from typing import Dict, List, TYPE_CHECKING, Set, Union
import asyncio
import re
import aiofiles
from aiofiles import os as aiofiles_os
import os
import json
from datetime import datetime
from zoneinfo import ZoneInfo
import traceback
from loguru import logger
from app.utils.vueRef import RefType
from app.core.config import settings
from app.schemas.vfnode import VFlowData
from app.schemas.fanode import FARunStatus
from app.services.messageMgr import ALL_MESSAGES_MGR
from app.schemas.farequest import (
    ValidationError,
    FANodeUpdateType,
    FANodeUpdateData,
    SSEResponse,
    SSEResponseData,
    SSEResponseType,
    FAWorkflowNodeResult,
    FAWorkflowResult,
    FAWorkflow,
)
from app.db.session import get_db_ctxmgr
from app.models.fastore import (
    FAWorkflowModel,
    FAReleasedWorkflowModel,
    FANodeCacheModel,
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
    RefItemValue,
)
from sqlalchemy import select, update, exc, exists, delete
from sqlalchemy.orm import selectinload

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
        pass

    def addNode(self, nid, node: "FABaseNode"):
        self.nodes[nid] = node
        pass

    def rmNode(self, nid):
        if nid in self.nodes:
            del self.nodes[nid]
        pass

    def getNode(self, request_nid: str) -> Union["FABaseNode", None]:
        return self.nodes.get(request_nid, None)

    async def getRefData(self, request_nid: str, refvalue: str):
        """
        根据curnid获取相对应层级的refdata数据
        针对Ref数据会自动解包，返回原始数据
        """
        # 获取cur节点的层级 =======================================
        cur_level = getNestedLayout(request_nid)
        # 获取ref节点的层级 =======================================
        refdata = RefItemValue.model_validate_json(refvalue)
        ref_level = getNestedLayout(refdata.nid)

        assert len(ref_level) <= len(cur_level), "层级不匹配"
        for i in range(len(ref_level)):
            ref_level[i] = cur_level[i]
        re_nid, _ = regexMatchNodeId(refdata.nid)
        ref_replace_nid = concatNestedNodeId(re_nid, ref_level)
        ref_node = self.getNode(ref_replace_nid)
        ref_data: VFNodeContentData = await ref_node.getContentByPath(
            request_nid,
            refdata.path,
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
        pass

    async def stop(self):
        self.cancel_event.set()
        # 取消所有关联任务
        tasks = list(self.running_tasks)
        self.running_tasks.clear()
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        pass

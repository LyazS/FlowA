from typing import List, Dict, Optional, TYPE_CHECKING, Any, cast, Union
from abc import ABC, abstractmethod
import asyncio
import re
from pydantic import BaseModel
import traceback
import json
import copy
from loguru import logger
from app.schemas.VFNodeInterface import FromInnerPath, VFNodeContentData
from app.schemas.fanode import FARunStatus, FANodeWaitType
from app.schemas.vfnode import VFNodeInfo
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
    FAWorkflowNodeRequest,
    FAWorkflowOperationResponse,
    FAProgressRequestType,
)
from app.utils.tools import reduceGet, generateCacheKey
from app.services.messageMgr import ALL_MESSAGES_MGR
from app.services.taskMgr import ALL_TASKS_MGR
from app.nodes.BaseNode import FABaseNode
from app.services.CacheMgr import GOLBAL_CACHE_MGR

if TYPE_CHECKING:
    from app.services.FARunner import FARunner
    from app.services.FAValidator import FAValidator


class FANodeWaitStatus(BaseModel):
    nid: str
    output: str
    pass


class NodeCancelException(asyncio.CancelledError):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class FATaskNode(FABaseNode):
    def __init__(self, wid: str, nodeinfo: VFNodeInfo, runner: "FARunner"):
        super().__init__(wid, nodeinfo, runner)
        # 本节点的完成事件
        self.doneEvent = asyncio.Event()
        # 其他节点的输出handle的状态
        self.waitStatus: List[FANodeWaitStatus] = []
        # 其他节点的doneEvent会存在该节点的waitEvents列表里
        self.waitEvents: List[asyncio.Event] = []
        self.waitType = FANodeWaitType.AND
        # 该节点的输出handle的状态
        self.outputStatus: Dict[str, FARunStatus] = {
            oname: FARunStatus.Pending for oname in self.data.Connections.Outputs.keys()
        }
        pass

    def addPreNode(self, prenode: "FATaskNode", outhandle: str):
        # 在处理之前记得调用父类的addPreNode方法
        super().addPreNode(prenode, outhandle)
        """
        这里FATaskNode只接受前导节点也是FATaskNode
        """
        if not isinstance(prenode, FATaskNode):
            raise TypeError("前导节点必须是FATaskNode")
        self.waitEvents.append(prenode.doneEvent)
        self.waitStatus.append(
            FANodeWaitStatus(
                nid=prenode.id,
                output=outhandle,
            )
        )
        pass

    async def invoke(self):
        try:
            logger.debug(f"invoke {self.data.Label} {self.id}")

            runner = self.runner()
            if runner is None:
                logger.error(f"runner is None {self.data.Label} {self.id}")
                raise NodeCancelException("runner is None")
            # ===============================================================
            # 等待前导节点完成 ================================================
            # ===============================================================
            all_events_task = asyncio.gather(
                *(event.wait() for event in self.waitEvents),
                return_exceptions=False,  # 如果任一事件抛出异常，则整体失败
            )
            cancel_task = asyncio.create_task(runner.cancel_event.wait())
            done, pending = await asyncio.wait(
                [
                    all_events_task,
                    cancel_task,
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )
            if cancel_task in done:
                raise NodeCancelException("cancel event")
            logger.debug(f"wait done {self.data.Label} {self.id}")

            if len(self.waitStatus) > 0:
                # 如果是AND，要求不能出现任何error或cancel状态
                waitFunc = all if self.waitType == FANodeWaitType.AND else any
                preNodeSuccess = []
                for thiswstatus in self.waitStatus:
                    thenode: FATaskNode = runner.getNode(thiswstatus.nid)
                    thisowstatus = thenode.outputStatus[thiswstatus.output]
                    preNodeSuccess.append(thisowstatus == FARunStatus.Success)

                canRunNode = waitFunc(preNodeSuccess)
                # 前置节点出错或取消，本节点取消运行
                if not canRunNode:
                    # 找出是哪个节点出错或取消
                    for thiswstatus in self.waitStatus:
                        thenode: FATaskNode = runner.getNode(thiswstatus.nid)
                        thisowstatus = thenode.outputStatus[thiswstatus.output]
                        logger.debug(
                            f"pre node error or cancel {self.data.Label} {self.id} due to {thiswstatus.nid} {thiswstatus.output} {thisowstatus}"
                        )

                    raise NodeCancelException("前置节点出错或取消，本节点取消运行")
            logger.debug(f"can run {self.data.Label} {self.id}")
            # ===============================================================

            # ===============================================================
            # 设置运行状态（Running） ========================================
            # ===============================================================
            self.setAllOutputStatus(FARunStatus.Running)
            self.putNodeStatus(FARunStatus.Running)
            updateDatas = None

            # ===============================================================
            # 读取缓存 =======================================================
            # 决定新运行还是使用缓存
            # ===============================================================
            # 嵌套节点不需要缓存，因为嵌套节点并不实际执行内容，只是控制流程
            isUseCache = False
            cacheKey = self.getCacheKey(self.id)
            if cacheKey and not self.data.is_nested_node():
                if nodecache := await GOLBAL_CACHE_MGR.get(self.wid, cacheKey):
                    self.loadCache(nodecache)
                    isUseCache = True
                logger.debug(f"cache hit {self.data.Label} {self.id} {cacheKey}")

            # logger.debug(f"get cache {self.data.Label} {self.id} {cacheKey}")
            if not isUseCache:
                # 前置节点全部成功，本节点开始运行
                updateDatas = await self.run()
                if cacheKey:
                    await GOLBAL_CACHE_MGR.set(self.wid, cacheKey, self.generateCache())
            # ===============================================================

            # 运行成功
            logger.debug(f"run success {self.data.Label} {self.id}")
            # self.setAllOutputStatus(FANodeStatus.Success)
            # 各个输出handle的成功需要由子类函数来设置
            self.putNodeStatus(FARunStatus.Success)
            nodeUpdateDatas = []
            if updateDatas:
                nodeUpdateDatas.extend(updateDatas)
                pass
            if len(nodeUpdateDatas) > 0:
                ALL_MESSAGES_MGR.put(
                    f"{self.wid}/{FAProgressRequestType.VFlowUI}",
                    SSEResponse(
                        event=SSEResponseType.updatenode,
                        data=SSEResponseData(
                            nid=self.id,
                            oriid=self.oriid,
                            data=nodeUpdateDatas,
                        ),
                    ),
                )
            pass
        except asyncio.CancelledError as e:
            if isinstance(e, NodeCancelException):
                logger.debug(
                    f"node cancel {self.data.Label} {self.id} due to {e.message}"
                )
            else:
                logger.debug(
                    f"node cancel {self.data.Label} {self.id} due to runner cancel"
                )
            self.setAllOutputStatus(FARunStatus.Canceled)
            self.putNodeStatus(FARunStatus.Canceled)
            pass
        except Exception as e:
            error_message = traceback.format_exc()
            logger.error(f"node error {self.data.Label} {error_message} {self.id}")
            self.setAllOutputStatus(FARunStatus.Error)
            self.putNodeStatus(FARunStatus.Error)
        finally:
            # 确保挂起任务被取消
            if all_events_task and not all_events_task.done():
                logger.debug(f"cancel all_events_task {self.data.Label} {self.id}")
                all_events_task.cancel()
                try:
                    await all_events_task
                except asyncio.CancelledError:
                    pass
            self.doneEvent.set()
        pass

    def setAllOutputStatus(self, status: FARunStatus):
        for oname in self.outputStatus:
            self.outputStatus[oname] = status
        pass

    def setOutputStatus(self, oname: str, status: FARunStatus):
        self.outputStatus[oname] = status
        pass

    def putNodeStatus(self, status: FARunStatus):
        self.runStatus = status
        ALL_MESSAGES_MGR.put(
            f"{self.wid}/{FAProgressRequestType.VFlowUI}",
            SSEResponse(
                event=SSEResponseType.updatenode,
                data=SSEResponseData(
                    nid=self.id,
                    oriid=self.oriid,
                    data=[
                        FANodeUpdateData(
                            type=FANodeUpdateType.overwrite,
                            path=["State", "Status"],
                            data=status,
                        )
                    ],
                ),
            ),
        )
        pass

    # 需要子类实现的函数 ===============================================================
    def getCacheKey(self, request_nid: str):
        if self.cacheKey:
            return self.cacheKey
        parentNode = self.runner().getNode(self.parentNode)
        parentCacheKey = parentNode.getCacheKey(self.id) if parentNode else None
        preNodeCacheKeys = {}
        for prenode in self.preNodes:
            if preNode := self.runner().getNode(prenode.nid):
                if preNodeCacheKey := preNode.getCacheKey(self.id):
                    preNodeCacheKeys[prenode.nid] = preNodeCacheKey
                else:
                    # 如果前置节点没有缓存键，则后续也要跳过缓存
                    return None
        data = {
            "wid": self.wid,
            "id": self.id,
            "data": {
                "Connections": self.data.Connections.model_dump(),
                "Payloads": self.data.Payloads.model_dump(),
                "Results": None,
                "Config": self.data.Config.model_dump(),
                "Attaching": (
                    self.data.Attaching.model_dump() if self.data.Attaching else None
                ),
                "Nesting": (
                    self.data.Nesting.model_dump() if self.data.Nesting else None
                ),
            },
            "parentCacheKey": parentCacheKey,
            "preNodeCacheKeys": preNodeCacheKeys,
        }
        self.cacheKey = generateCacheKey(data)
        return self.cacheKey

    async def getContentByPath(
        self, request_nid: str, path: FromInnerPath
    ) -> VFNodeContentData:
        return self.data.getContent(path.ContentName).ById[path.ContentId]

    async def run(self) -> List[FANodeUpdateData]:
        self.setAllOutputStatus(FARunStatus.Success)
        pass

    async def getCurData(self) -> Optional[List[FANodeUpdateData]]:
        return [
            FANodeUpdateData(
                type=FANodeUpdateType.overwrite,
                path=["State", "Status"],
                data=self.runStatus,
            )
        ]

    async def validate(self, validator: "FAValidator") -> Optional[ValidationError]:
        return None

    async def processRequest(
        self,
        request: dict,
    ) -> Optional[FAWorkflowOperationResponse]:
        return None

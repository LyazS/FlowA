from typing import List, Dict, Optional, TYPE_CHECKING, Any, cast, Union
from abc import ABC, abstractmethod
import asyncio
import re
from pydantic import BaseModel
import traceback
import json
import copy
from PIL import Image
from loguru import logger
from app.schemas.VFNodeInterface import (
    VarType,
    FromInnerPath,
    VFNodeContentData,
    VFNodeContents,
)
from app.schemas.VFlowRunData import (
    FARunStatus,
    FANodeWaitType,
    VFNodeCacheKey,
    VFNodeCacheKeyBefore,
    VFNodeCacheKeyAfter,
)
from app.schemas.VFlowData import VFNodeInfo
from app.schemas.farequest import (
    ValidationError,
    FANodeUpdateType,
    FANodeUpdateData,
    SSEResponse,
    SSEResponseData,
    SSEResponseType,
    FAWorkflow,
    FAWorkflowNodeRequest,
    FAWorkflowOperationResponse,
    FAProgressRequestType,
)
from app.utils.tools import reduceGet
from app.nodes.BaseNode import FABaseNode
from app.services.messageMgr import ALL_MESSAGES_MGR
from app.utils.cacheKey import buildCache4GenerateKey

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


class ResultTypeError(Exception):
    def __init__(self, messages: List[str]):
        self.messages = messages
        super().__init__(self.messages)


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
            oname: FARunStatus.Pending for oname in self.data.Connections.Outputs.Order
        }
        # 缓存键
        self.cacheKey = None
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

    def checkResultType(self):
        """
        检查Result的Data类型是否符合Type
        """
        allok = []
        allmsg = []
        for rid in self.data.Results.Order:
            isok = False
            res_data = self.data.Results.ById[rid].Data.value
            if self.data.Results.ById[rid].Type == VarType.Any:
                isok = True
            elif self.data.Results.ById[rid].Type == VarType.String:
                isok = isinstance(res_data, str)
            elif self.data.Results.ById[rid].Type == VarType.Integer:
                isok = isinstance(res_data, int)
            elif self.data.Results.ById[rid].Type == VarType.Number:
                isok = isinstance(res_data, (int, float))
            elif self.data.Results.ById[rid].Type == VarType.Boolean:
                isok = isinstance(res_data, bool)
            elif self.data.Results.ById[rid].Type == VarType.List:
                isok = isinstance(res_data, list)
            elif self.data.Results.ById[rid].Type == VarType.Dict:
                isok = isinstance(res_data, dict)
            elif self.data.Results.ById[rid].Type == VarType.Image:
                isok = isinstance(res_data, Image.Image)
            elif self.data.Results.ById[rid].Type == VarType.File:
                isok = isinstance(res_data, bytes)
            if not isok:
                label = self.data.Results.ById[rid].Label
                errmsg = f"Result [{label}] type should be [{self.data.Results.ById[rid].Type}] but {type(res_data)} found"
                logger.error(errmsg)
                allmsg.append(errmsg)
            allok.append(isok)
        if not all(allok):
            raise ResultTypeError(allmsg)
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
            self.pushNodeStatus(FARunStatus.Running)
            updateDatas = None

            # ===============================================================
            # 读取缓存 =======================================================
            # 决定新运行还是使用缓存
            # ===============================================================
            # 一般来说嵌套节点不需要缓存，因为嵌套节点并不实际执行内容，只是控制流程
            isUseCache = False
            cacheKey = self.getCacheKey(self.id)
            if cacheKey.Before == VFNodeCacheKeyBefore.Load:
                if nodecache := await self.runner().getCache(self.id, cacheKey.Key):
                    isUseCache = self.loadCache(nodecache)
                    logger.debug(
                        f"cache hit {self.data.Label} {self.id} {cacheKey.Key}"
                    )

            if not isUseCache:
                # 前置节点全部成功，本节点开始运行
                updateDatas = await self.run()
                self.checkResultType()
                if cacheKey.Key and cacheKey.After == VFNodeCacheKeyAfter.Save:
                    await self.runner().setCache(
                        self.id,
                        cacheKey.Key,
                        self.generateCache(),
                        isCommit=False,
                    )
            # ===============================================================

            # 运行成功
            logger.debug(f"run success {self.data.Label} {self.id}")
            # self.setAllOutputStatus(FANodeStatus.Success)
            # 各个输出handle的成功需要由子类函数来设置
            self.pushNodeStatus(FARunStatus.Success)
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
            self.pushNodeStatus(FARunStatus.Canceled)
            pass
        except ResultTypeError as e:
            logger.error(f"node error {self.data.Label} {self.id}")
            for msg in e.messages:
                logger.error(msg)
            self.setAllOutputStatus(FARunStatus.Error)
            self.pushNodeStatus(FARunStatus.Error)
            self.pushNodeErrors(e.messages)
        except Exception as e:
            error_message = traceback.format_exc()
            msg = f"node error {self.data.Label} {error_message} {self.id}"
            logger.error(msg)
            self.setAllOutputStatus(FARunStatus.Error)
            self.pushNodeStatus(FARunStatus.Error)
            self.pushNodeErrors([msg])
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

    def pushNodeStatus(self, status: FARunStatus):
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
    def pushNodeErrors(self, error_messages: List[str]):
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
                            path=["State", "Errors"],
                            data=error_messages,
                        ),
                    ],
                ),
            ),
        )
        pass
    # 需要子类实现的函数 ===============================================================

    def getCacheKey(self, request_nid: str) -> VFNodeCacheKey:
        if not self.cacheKey:
            self.cacheKey = buildCache4GenerateKey(self)
        return self.cacheKey

    def generateCache(self) -> Dict | None:
        """
        生成缓存
        """
        cache = {
            "outputStatus": self.outputStatus,
            "Results": self.data.Results.model_dump(),
        }
        return cache

    def loadCache(self, cache: Dict) -> None:
        """
        从缓存恢复当前节点的数据
        """
        if "Results" not in cache:
            logger.warning("Cache键 [Results] 不存在")
            return False
        cache_results = VFNodeContents.model_validate(cache["Results"])
        if set(self.data.Results.ById.keys()) != set(cache_results.ById.keys()):
            logger.warning("Cache结果集不完全匹配当前节点结果集")
            return False
        for rid in self.data.Results.ById.keys():
            cache_result = cache_results.ById[rid]
            self.data.Results.ById[rid].Label = cache_result.Label
            self.data.Results.ById[rid].Type = cache_result.Type
            self.data.Results.ById[rid].Data.value = cache_result.Data.value
            self.data.Results.ById[rid].Config = cache_result.Config
            self.data.Results.ById[rid].Hid = cache_result.Hid
            self.data.Results.ById[rid].Did = cache_result.Did
            self.data.Results.ById[rid].UiType = cache_result.UiType

        # 检查cache["outputStatus"]是否完全对应上self.outputStatus
        if (
            ("outputStatus" not in cache)
            or (not isinstance(cache["outputStatus"], dict))
            or (set(cache["outputStatus"].keys()) != set(self.outputStatus.keys()))
        ):
            logger.warning("Cache outputStatus不完全匹配当前节点outputStatus")
            return False
        for status_name in self.outputStatus:
            self.outputStatus[status_name] = cache["outputStatus"][status_name]
        pass
        return True

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

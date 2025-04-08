from typing import List, Dict, Optional, TYPE_CHECKING, Any, Union
from abc import ABC, abstractmethod
from weakref import ref
import copy
from loguru import logger
from app.utils.tools import generateCacheKey
from app.schemas.fanode import (
    FARunStatus,
    FANodeWaitType,
    ConnectOption_Var,
    ConnectOption_Node,
)
from app.schemas.VFNodeClass import VFNode, create_vf_node_from_data
from app.schemas.VFNodeInterface import FromInnerPath, VFNodeContentData
from app.schemas.VFlowData import VFNodeInfo
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
    FAWorkflowOperationResponse,
)

if TYPE_CHECKING:
    from app.services.FARunner import FARunner
    from app.services.FAValidator import FAValidator


class FABaseNode(ABC):
    def __init__(self, wid: str, nodeinfo: VFNodeInfo, runner: "FARunner"):
        if runner:
            self.runner = ref(runner)
        else:
            self.runner = None
        cpnodeinfo = copy.deepcopy(nodeinfo)
        self.wid = wid
        self.id = cpnodeinfo.id
        self.oriid = copy.deepcopy(cpnodeinfo.id)
        self.data: VFNode = create_vf_node_from_data(cpnodeinfo.data)
        self.ntype: str = cpnodeinfo.data.NType
        self.parentNode = cpnodeinfo.parentNode

        # 该节点的运行状态
        self.runStatus = FARunStatus.Pending

        """
        节点的缓存键，需要包括的内容
        wid
        id
        data里的
            Connections
            Payloads
            Results
                这里要去掉Data
            Config
            Attaching
            Nesting
        parentNode的缓存键
        前导节点的缓存键
        """
        self.cacheKey = None

        pass

    def getCacheKey(self):
        if self.cacheKey:
            return self.cacheKey
        parentNode = self.runner().getNode(self.parentNode)
        parentCacheKey = parentNode.getCacheKey() if parentNode else None
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
            "preNodeCacheKeys": {},
        }
        self.cacheKey = generateCacheKey(data)
        return self.cacheKey

    def store(self):
        return FAWorkflowNodeResult(
            tid=self.tid,
            id=self.id,
            oriid=self.oriid,
            data=self.data,
            ntype=self.ntype,
            parentNode=self.parentNode,
            runStatus=self.runStatus,
        )

    def restore(self, data: FAWorkflowNodeResult):
        self.tid = data.tid
        self.id = data.id
        self.oriid = data.oriid
        self.data = data.data
        self.ntype = data.ntype
        self.parentNode = data.parentNode
        self.runStatus = data.runStatus
        pass

    @abstractmethod
    def addPreNode(self, prenode: "FABaseNode"):
        pass

    @abstractmethod
    async def invoke(self):
        pass

    @abstractmethod
    async def getCurData(self) -> Optional[List[FANodeUpdateData]]:
        return []

    @abstractmethod
    async def getContentByPath(
        self, request_nid: str, path: FromInnerPath
    ) -> VFNodeContentData:
        """
        返回Payloads或Results的内容，为VFNodeContentData结构
        """
        return None

    @abstractmethod
    async def validate(self, validator: "FAValidator") -> Optional[ValidationError]:
        return None

    @abstractmethod
    async def processRequest(
        self,
        request: dict,
    ) -> Optional[FAWorkflowOperationResponse]:
        """
        用于动态发送请求给节点处理
        """
        return None

    @staticmethod
    async def getNodeConfig():
        """
        节点的配置信息，例如可以获取LLM的模型列表
        """
        return None

    @staticmethod
    def getNodeCreateInfo() -> VFNode:
        """
        节点的创建信息
        """
        return None

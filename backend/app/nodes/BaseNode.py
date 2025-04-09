from typing import List, Dict, Optional, TYPE_CHECKING, Any, Union
from abc import ABC, abstractmethod
from pydantic import BaseModel
from weakref import ref
import copy
from loguru import logger
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


class FAPreNodeModel(BaseModel):
    nid: str
    handle: str
    pass


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

        # 该节点的运行状态
        self.runStatus = FARunStatus.Pending

        # 父节点原始id
        self.parentNode = cpnodeinfo.parentNode
        # 该节点的前导节点
        self.preNodes: List[FAPreNodeModel] = []

        """
        节点的缓存键，可能需要包括的内容
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

    def setNodeID(self, nodeid: str):
        """
        设置节点id，针对嵌套内的子节点很有用，可以重新设置id
        """
        self.id = nodeid
        pass

    def setParentNodeID(self, parentid: str):
        self.parentNode = parentid
        pass

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

    def addPreNode(self, prenode: "FABaseNode", outhandle: str):
        self.preNodes.append(FAPreNodeModel(nid=prenode.id, handle=outhandle))
        pass

    @abstractmethod
    def getCacheKey(self, request_nid: str):
        """
        针对请求节点，返回相应的缓存键
        """
        return None

    @abstractmethod
    async def invoke(self):
        pass

    @abstractmethod
    async def getCurData(self) -> Optional[List[FANodeUpdateData]]:
        return []

    @abstractmethod
    async def getContentByPath(
        self,
        request_nid: str,
        path: FromInnerPath,
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

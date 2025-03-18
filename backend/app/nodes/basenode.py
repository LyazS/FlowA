from typing import List, Dict, Optional, TYPE_CHECKING, Any
from abc import ABC, abstractmethod
from weakref import ref
import copy
from loguru import logger
from app.schemas.fanode import FARunStatus, FANodeWaitType, FANodeValidateNeed
from app.schemas.VFNodeClass import VFNode
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
        self.data: VFNode = copy.deepcopy(cpnodeinfo.data)
        self.ntype: str = cpnodeinfo.data.NType
        self.parentNode = cpnodeinfo.parentNode

        # 该节点的输出handle的状态
        self.outputStatus: Dict[str, FARunStatus] = {
            oname: FARunStatus.Pending for oname in self.data.Connections.Outputs.keys()
        }
        # 该节点的运行状态
        self.runStatus = FARunStatus.Pending

        # 该节点需求的验证内容
        self.validateNeededs: List[FANodeValidateNeed] = []
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

    @abstractmethod
    async def invoke(self):
        pass

    @abstractmethod
    async def getCurData(self) -> Optional[List[FANodeUpdateData]]:
        return []

    @abstractmethod
    async def getRefData(self, refdata: str) -> Any:
        return None

    @abstractmethod
    def validate(
        self,
        validateVars: Dict[FANodeValidateNeed, Any],
    ) -> Optional[ValidationError]:
        return None

    async def processRequest(
        self,
        request: dict,
    ) -> Optional[FAWorkflowOperationResponse]:
        return None

    @staticmethod
    def getNodeConfig():
        return None

    @staticmethod
    def getNodeCreateInfo() -> VFNode:
        return None

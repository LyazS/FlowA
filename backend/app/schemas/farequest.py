from typing import List, Optional, Any, Union, Dict
import json
from datetime import datetime
from pydantic import BaseModel
from enum import Enum
from .vfnode import VFlowData, VFNodeData
from .fanode import FARunStatus


class VarItem(BaseModel):
    nodeId: str
    nlabel: str
    dpath: List[str]
    dlabel: str
    dkey: str
    dtype: str


class VarSelectOption(BaseModel):
    label: str
    value: str


class ValidationError(BaseModel):
    nid: str
    errors: List[str]  # 可能存在多条错误信息。如果isValid为True，则messages应该为空。
    pass


class FANodeUpdateType(Enum):
    overwrite = "overwrite"
    append = "append"
    remove = "remove"
    dontcare = "dontcare"
    pass


class FANodeUpdateData(BaseModel):
    type: FANodeUpdateType
    path: Optional[List[Union[str, int]]] = None
    data: Optional[Any] = None
    pass


class SSEResponseType(Enum):
    updatenode = "updatenode"
    batchupdatenode = "batchupdatenode"
    internalerror = "internalerror"
    flowfinish = "flowfinish"
    pass


class SSEResponseData(BaseModel):
    nid: str
    oriid: str
    data: List[FANodeUpdateData]
    pass


class SSEResponse(BaseModel):
    event: SSEResponseType
    data: Union[SSEResponseData, List[SSEResponseData], None] = None
    pass

    def toSSEResponse(self):
        data = None
        if isinstance(self.data, SSEResponseData):
            data = self.data.model_dump_json()
        elif isinstance(self.data, list):
            model_datas = []
            for d in self.data:
                d_json = d.model_dump_json()
                model_datas.append(json.loads(d_json))
            # model_datas = [json.loads(d.model_dump_json()) for d in self.data]
            data = json.dumps(model_datas)
        return {
            "event": self.event.value,
            "data": data,
        }

    pass


class FAWorkflowNodeResult(BaseModel):
    tid: str
    id: str
    oriid: str
    data: VFNodeData
    ntype: str
    parentNode: Optional[str]
    runStatus: FARunStatus
    pass


class FAWorkflowResult(BaseModel):
    tid: str
    usedvflow: Optional[dict]
    noderesult: Optional[List[FAWorkflowNodeResult]]
    status: FARunStatus
    starttime: datetime
    endtime: datetime
    pass


class FAWorkflow(BaseModel):
    wid: Optional[str] = None
    name: Optional[str] = None
    vflow: Optional[dict] = None
    pass


class FAWorkflowCreateType(Enum):
    new = "new"
    upload = "upload"
    release = "release"
    pass


class FAWorkflowRunType(Enum):
    Full = "Full"
    Incremental = "Incremental"
    Api = "Api"
    Stop = "Stop"
    pass


class FAWorkflowRunRequest(BaseModel):
    type: FAWorkflowRunType
    wid: str
    vflow: Optional[dict] = None
    pass


class FAWorkflowRunReqType(Enum):
    validation = "validation"
    isrunning = "isrunning"
    internalerror = "internalerror"
    success = "success"
    pass


class FAWorkflowRunResponse(BaseModel):
    type: FAWorkflowRunReqType
    validation_errors: List[ValidationError] = None
    pass


class FAWorkflowCreateRequest(BaseModel):
    type: FAWorkflowCreateType
    wid: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    vflow: Optional[dict] = None
    pass


class FAWorkflowLocation(Enum):
    wfname = "wfname"
    rwfname = "rwfname"
    rwfdescription = "rwfdescription"
    vflow = "vflow"
    release = "release"
    allReleases = "allReleases"
    pass


class FAWorkflowUpdateItem(BaseModel):
    location: FAWorkflowLocation
    data: Optional[Any] = None
    rwid: Optional[str] = None
    pass


class FAWorkflowUpdateRequset(BaseModel):
    wid: str
    items: List[FAWorkflowUpdateItem]
    pass


class FAWorkflowReadRequest(BaseModel):
    wid: str
    locations: List[FAWorkflowLocation]
    rwid: Optional[str] = None
    pass


class FAWorkflowDeleteRequest(BaseModel):
    wid: str
    rwid: Optional[str] = None
    pass


class FAWorkflowInfo(BaseModel):
    wid: str
    name: str
    lastModified: Optional[datetime]
    pass


class FAReleaseWorkflowInfo(BaseModel):
    rwid: str
    releaseTime: datetime
    name: str
    description: str
    pass


class FAWorkflowNodeRequest(BaseModel):
    wid: str
    nid: str
    request: dict
    pass


class FAWorkflowOperationType(Enum):
    success = "success"
    error = "error"
    pass


class FAWorkflowOperationResponse(BaseModel):
    type: FAWorkflowOperationType
    message: Optional[str] = None
    data: Optional[Any] = None
    pass


class FAProgressRequestType(Enum):
    VFlowUI = "VFlowUI"
    JinJa = "JinJa"
    pass


class FAProgressRequest(BaseModel):
    type: FAProgressRequestType
    wid: str
    selected_nids: Optional[List[str]] = None
    pass

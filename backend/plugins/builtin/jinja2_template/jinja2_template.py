from typing import List, Dict, Optional, TYPE_CHECKING, Any
from loguru import logger
import asyncio
import traceback
from app.schemas.VFNodeClass import VFNode
from app.schemas.VFlowData import VFNodeInfo
from app.schemas.VFlowRunData import FARunStatus
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
    FromInnerPath,
    RefVarItem,
)
from app.schemas.farequest import (
    ValidationError,
    FANodeUpdateType,
    FANodeUpdateData,
    SSEResponse,
    SSEResponseData,
    SSEResponseType,
    FAWorkflowOperationResponse,
    FAProgressRequestType,
    FAWorkflowOperationType,
)
from app.utils.vueRef import serialize_ref, RefOptions, RefTriggerData
from app.services.messageMgr import ALL_MESSAGES_MGR
from app.schemas.VFlowRunData import VFNodeCacheKey
from app.services.FARunner import FARunner
from app.services.FAValidator import FAValidator
from ..UI_Components.UI_InputVars import InputVarModel, VarType


class Jinja2Template(FABaseNode):
    def __init__(self, wid: str, nodeinfo: VFNodeInfo, runner: "FARunner"):
        super().__init__(wid, nodeinfo, runner)
        self.runStatus = FARunStatus.Passive
        self.inReporting = False
        pass

    def report(
        self,
        triggerdata: RefTriggerData,
        key,
        wid,
        nid,
        oriid,
    ):
        if not self.inReporting:
            return
        ALL_MESSAGES_MGR.put(
            f"{wid}/{FAProgressRequestType.JinJa}",
            SSEResponse(
                event=SSEResponseType.updatenode,
                data=SSEResponseData(
                    nid=nid,
                    oriid=oriid,
                    data=[
                        FANodeUpdateData(
                            type=FANodeUpdateType.dontcare,
                            path=[key],
                            data=RefTriggerData(
                                path=triggerdata.path,
                                operation=triggerdata.operation,
                                new_value=serialize_ref(triggerdata.new_value),
                                old_value=serialize_ref(triggerdata.old_value),
                            ),
                        )
                    ],
                ),
            ),
        )
        pass

    def addPreNode(self, prenode: "FABaseNode"):
        pass

    def getCacheKey(self, request_nid):
        return VFNodeCacheKey()

    def generateCache(self) -> Dict | None:
        return None

    def loadCache(self, cache: Dict) -> None:
        pass

    async def getContentByPath(
        self, request_nid: str, path: FromInnerPath
    ) -> VFNodeContentData:
        return None

    async def invoke(self):
        try:
            runner = self.runner()
            if runner is None:
                logger.error(f"runner is None {self.data.Label} {self.id}")
                raise asyncio.CancelledError("runner is None")

            node_payloads = self.data.Payloads
            D_INPUT_VARS: VFNodeContentData = node_payloads.ById["D_INPUT_VARS"]
            for var_dict in D_INPUT_VARS.Data.value:
                var = InputVarModel.model_validate(var_dict)
                if var.type == VarType.Ref:
                    refdata = RefVarItem.model_validate_json(var.valueStr)
                    thenode = runner.getNode(refdata.Nid)
                    (
                        await thenode.getContentByPath(
                            self.id,
                            refdata.Path,
                        )
                    ).Data.add_dependency(
                        lambda triggerdata, key=var.key, wid=self.wid, nid=self.id, oriid=self.oriid: (
                            self.report(
                                triggerdata,
                                key,
                                wid,
                                nid,
                                oriid,
                            )
                        )
                    )
                    pass

        except Exception as e:
            errmsg = traceback.format_exc()
            logger.error(f"执行Jinja2节点{self.id}出错{str(errmsg)}")
            pass
        pass

    async def getCurData(self) -> Optional[List[FANodeUpdateData]]:
        curData = []
        node_payloads = self.data.Payloads
        D_INPUT_VARS: VFNodeContentData = node_payloads.ById["D_INPUT_VARS"]
        for var_dict in D_INPUT_VARS.Data.value:
            var = InputVarModel.model_validate(var_dict)
            curData.append(
                FANodeUpdateData(
                    type=FANodeUpdateType.dontcare,
                    path=[var.key],
                    data=RefTriggerData(
                        path=[],
                        operation=RefOptions.Set,
                        new_value=await InputVarModel.get_value(
                            var,
                            self.id,
                            self.runner().getRefData,
                        ),
                        old_value=None,
                    ),
                )
            )
        return curData

    async def processRequest(
        self,
        request: dict,
    ) -> Optional[FAWorkflowOperationResponse]:
        if request.get("action") == "start":
            self.inReporting = True
        else:
            self.inReporting = False
        return FAWorkflowOperationResponse(
            type=FAWorkflowOperationType.success,
            message="start report",
        )

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

            D_INPUT_VARS: VFNodeContentData = node_payloads.ById["D_INPUT_VARS"]
            for var_dict in D_INPUT_VARS.Data.value:
                var = InputVarModel.model_validate(var_dict)
                if var.type == VarType.Ref and var.valueStr not in selfVars:
                    error_msgs.append(f"变量未定义{var.valueStr}")
        except Exception as e:
            errmsg = traceback.format_exc()
            error_msgs.append(f"获取内容失败{str(errmsg)}")
        if len(error_msgs) > 0:
            return ValidationError(nid=self.id, errors=error_msgs)
        return None

    @staticmethod
    def getNodeCreateInfo():
        thisnode = VFNode("basenode")
        thisnode.set_flag(VFNodeFlag.IsPassive)
        thisnode.set_size(80, 80)
        thisnode.add_handle(VFNodeConnectionType.Inputs, "input", "Input")
        thisnode.add_handle(VFNodeConnectionType.Self, "self")
        thisnode.add_handle_data(
            VFNodeConnectionType.Self,
            "self",
            VFNodeHandleData(
                Type=VFNodeConnectionDataType.FromOuter,
                HandleId="input",
            ),
        )
        thisnode.add_payload(
            VFNodeContentData(
                Label="输入变量",
                Type="List",
                Data=[
                    InputVarModel(key="arg1", valueStr="hello"),
                    InputVarModel(key="arg2", valueStr="world"),
                ],
                UiType="@/FlowABuiltin/UI_INPUT_VARS",
            ),
            payload_id="D_INPUT_VARS",
        )
        thisnode.add_payload(
            VFNodeContentData(
                Label="Jinja2模板",
                Type="String",
                Data="<p>{{ arg1 }}</p>\n<hr>\n<p>{{ arg2 }}</p>",
                UiType="@/FlowABuiltin/UI_CODE_EDITOR_DISABLED",
                Config=VFNodeContentDataConfig(Language="django"),
            ),
            payload_id="D_JINJA2_TEMPLATE",
        )
        return thisnode


# 必须存在
EXPORT_NODE = Jinja2Template

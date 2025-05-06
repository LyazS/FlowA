from typing import List, Dict, Optional, TYPE_CHECKING, Any, Union
import os
import io
import base64
import json
import traceback
from PIL import Image
from loguru import logger
from app.schemas.VFNodeClass import VFNode
from app.schemas.VFlowData import VFNodeInfo
from app.schemas.VFlowRunData import FARunStatus
from app.schemas.farequest import (
    ValidationError,
    FANodeUpdateType,
    FANodeUpdateData,
)
from app.nodes.BaseNode import FABaseNode
from app.nodes.TaskNode import FATaskNode
from app.uisdk import *
from app.schemas.VFNodeInterface import (
    VFNodeConnectionType,
    VFNodeFlag,
    VFNodeContentData,
    VFNodeHandleData,
    VFNodeConnectionDataType,
    VFNodeContentDataConfig,
    FromInnerPath,
    RefVarItem,
    VarType,
)
from app.services.FARunner import FARunner
from app.services.FAValidator import FAValidator
from app.api.file_mgr import WORKFLOW_DATA_DIR
from app.utils.tools import reduceGet


class CF_NodeVar(BaseModel):
    NodeId: str = ""
    FieldName: str = ""
    FieldType: VarType = VarType.String
    FieldValueStr: str = ""
    FieldValueRef: Optional[RefVarItem] = None
    pass


class CF_Workflow(BaseModel):
    Type: VarType = VarType.File
    ValueJson: Optional[UploadFileInfo] = None
    ValueRef: Optional[RefVarItem] = None
    pass


class ComfyUINetTool(FATaskNode):
    def __init__(self, wid: str, nodeinfo: VFNodeInfo, runner: "FARunner"):
        super().__init__(wid, nodeinfo, runner)
        pass

    async def validate(self, validator: "FAValidator") -> Optional[ValidationError]:
        error_msgs = []
        try:
            node_payloads = self.data.Payloads
            selfVars = await validator.getConnectionByPath(
                self.id,
                [
                    CONNECT_DATA_TO_SELECT,
                    VFNodeConnectionType.Self,
                    "self",
                ],
            )

            D_WORKFLOW = node_payloads.ById["D_WORKFLOW"]
            CF_Workflow_Data = CF_Workflow.model_validate(D_WORKFLOW.Data.value)
            if CF_Workflow_Data.Type == VarType.File:
                if not CF_Workflow_Data.ValueJson:
                    error_msgs.append("请上传工作流文件")
                else:
                    try:
                        json.loads(CF_Workflow_Data.ValueJson.File)
                        pass
                    except Exception as e:
                        error_msgs.append(f"工作流文件不是JSON格式: {str(e)}")
                        pass
            elif CF_Workflow_Data.Type == VarType.Ref:
                if (
                    not CF_Workflow_Data.ValueRef
                    or CF_Workflow_Data.ValueRef.model_dump_json() not in selfVars
                ):
                    error_msgs.append(f"引用变量{CF_Workflow_Data.ValueRef}不存在")
                    pass

            D_NODE_VAR = node_payloads.ById["D_NODE_VAR"]
            for var_item in D_NODE_VAR.Data.value:
                node_var = CF_NodeVar.model_validate(var_item)
                if node_var.NodeId == "":
                    error_msgs.append(f"节点变量缺少节点ID")
                    pass
                if node_var.FieldName == "":
                    error_msgs.append(f"节点变量缺少字段名")
                if node_var.FieldType == VarType.Ref:
                    if (
                        not node_var.FieldValueRef
                        or node_var.FieldValueRef.model_dump_json() not in selfVars
                    ):
                        error_msgs.append(
                            f"节点变量的引用变量{node_var.FieldValueRef}不存在"
                        )
            pass
        except Exception as e:
            errmsg = traceback.format_exc()
            error_msgs.append(f"获取内容失败{str(errmsg)}")

        if len(error_msgs) > 0:
            return ValidationError(nid=self.id, errors=error_msgs)
        return None

    async def run(self) -> List[FANodeUpdateData]:
        node_payloads = self.data.Payloads

        return []

    @staticmethod
    async def getNodeConfig():
        return {}

    @staticmethod
    def getNodeCreateInfo():
        thisnode = VFNode("basenode")
        thisnode.set_flag(VFNodeFlag.IsTask)
        thisnode.set_size(80, 80)

        # 添加输入和输出句柄
        thisnode.add_handle(VFNodeConnectionType.Inputs, "input", "INPUT")
        thisnode.add_handle(VFNodeConnectionType.Outputs, "output", "OUTPUT")
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
                Label="工作流",
                Type=VarType.Any,
                Data=CF_Workflow(),
                UiType="@/FlowABuiltinEx/UI_COMFYUI_WORKFLOW",
            ),
            payload_id="D_WORKFLOW",
        )
        thisnode.add_payload(
            VFNodeContentData(
                Label="节点变量",
                Type=VarType.List,
                Data=[],
                UiType="@/FlowABuiltinEx/UI_COMFYUI_NODE_VAR",
            ),
            payload_id="D_NODE_VAR",
        )
        thisnode.add_result_into_outputs(
            VFNodeContentData(
                Label="输出图像数组",
                Type=VarType.List,
                Data=[],
            ),
            handle_id="output",
            result_id="R_IMAGE",
        )
        thisnode.set_outputs_ui_type("@/FlowABuiltin/UI_TAG_OUTPUTS")

        return thisnode


# 必须存在
EXPORT_NODE = ComfyUINetTool

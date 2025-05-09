from typing import List, Dict, Optional, TYPE_CHECKING, Any, Union
import os
import io
import base64
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


class ImageReadData(BaseModel):
    Type: VarType = VarType.String
    ValueStr: str = ""
    ValueRef: Optional[RefVarItem] = None
    pass


class ImageRead(FATaskNode):
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

            D_IMAGE_PATH: VFNodeContentData = node_payloads.ById["D_IMAGE_PATH"]
            D_IMAGE_PATH_DATA = ImageReadData.model_validate(D_IMAGE_PATH.Data.value)
            if D_IMAGE_PATH_DATA.Type == VarType.Ref and (
                not D_IMAGE_PATH_DATA.ValueRef
                or D_IMAGE_PATH_DATA.ValueRef.model_dump_json() not in selfVars
            ):
                error_msgs.append(f"变量未定义{D_IMAGE_PATH_DATA.ValueRef}")
                pass
            if D_IMAGE_PATH_DATA.Type == VarType.String:
                # 检查路径是否存在
                if not os.path.exists(D_IMAGE_PATH_DATA.ValueStr):
                    error_msgs.append(f"图片文件路径不存在{D_IMAGE_PATH_DATA.ValueStr}")
                pass
        except Exception as e:
            errmsg = traceback.format_exc()
            error_msgs.append(f"获取内容失败{str(errmsg)}")

        if len(error_msgs) > 0:
            return ValidationError(nid=self.id, errors=error_msgs)
        return None

    async def run(self) -> List[FANodeUpdateData]:
        node_payloads = self.data.Payloads
        D_IMAGE_PATH: VFNodeContentData = node_payloads.ById["D_IMAGE_PATH"]
        D_IMAGE_PATH_DATA = ImageReadData.model_validate(D_IMAGE_PATH.Data.value)

        dstPath = None
        if D_IMAGE_PATH_DATA.Type == VarType.Ref:
            dstPath = await self.runner().getRefData(
                self.id, D_IMAGE_PATH_DATA.ValueRef
            )
        elif D_IMAGE_PATH_DATA.Type == VarType.String:
            dstPath = D_IMAGE_PATH_DATA.ValueStr

        img = Image.open(dstPath)
        self.data.Results.ById["R_IMAGE"].Data.value = img
        self.setAllOutputStatus(FARunStatus.Success)
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
        # 添加图片路径的payload
        thisnode.add_payload(
            VFNodeContentData(
                Label="图片路径",
                Type=VarType.Any,
                Data=ImageReadData(),
                UiType="@/FlowABuiltinEx/UI_IMAGE_READ_PATH",
            ),
            payload_id="D_IMAGE_PATH",
        )

        # 添加图片输出的result
        thisnode.add_result_into_outputs(
            VFNodeContentData(
                Label="图片",
                Type=VarType.Image,
                Data=None,
            ),
            handle_id="output",
            result_id="R_IMAGE",
        )
        thisnode.set_outputs_ui_type("@/FlowABuiltin/UI_TAG_OUTPUTS")
        return thisnode


# 必须存在
EXPORT_NODE = ImageRead

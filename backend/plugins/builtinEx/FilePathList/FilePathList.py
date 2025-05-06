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


"""
单选
1. 目录模式
    目录输入框
    文件名输入框（支持通配符，如果快速选择为空则出现）
    快速选择复选框：图像、视频（如果文件名输入框为空则出现）
2. 正则表达式
    输入框
递归子目录开关
"""


class FilePathListType(StrEnum):
    DIR = "DIR"
    REGEX = "REGEX"
    pass


class FilePathQuickSelect(StrEnum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    pass


class FilePathListData(BaseModel):
    Type: FilePathListType = FilePathListType.DIR
    Dir: str = ""
    FileName: str = ""
    QuickSelect: List[FilePathQuickSelect] = []
    Regex: str = ""
    Recursive: bool = False
    pass


class FilePathList(FATaskNode):
    def __init__(self, wid: str, nodeinfo: VFNodeInfo, runner: "FARunner"):
        super().__init__(wid, nodeinfo, runner)
        pass

    async def validate(self, validator: "FAValidator") -> Optional[ValidationError]:
        error_msgs = []
        try:

            pass
        except Exception as e:
            errmsg = traceback.format_exc()
            error_msgs.append(f"获取内容失败{str(errmsg)}")

        if len(error_msgs) > 0:
            return ValidationError(nid=self.id, errors=error_msgs)
        return None

    async def run(self) -> List[FANodeUpdateData]:

        return []

    @staticmethod
    async def getNodeConfig():
        return {}

    @staticmethod
    def getNodeCreateInfo():
        thisnode = VFNode("basenode")
        thisnode.set_flag(VFNodeFlag.IsTask)
        thisnode.set_size(80, 80)

        thisnode.add_handle(VFNodeConnectionType.Outputs, "output", "OUTPUT")

        thisnode.add_payload(
            VFNodeContentData(
                Label="目录选择",
                Type=VarType.Any,
                Data=FilePathListData(),
                UiType="@/FlowABuiltinEx/UI_FILE_PATH_LIST",
            ),
            payload_id="D_FILE_PATH_LIST",
        )
        
        thisnode.add_result_into_outputs(
            VFNodeContentData(
                Label="输出路径数组",
                Type=VarType.List,
                Data=[],
            ),
            handle_id="output",
            result_id="R_PATHS",
        )
        thisnode.set_outputs_ui_type("@/FlowABuiltin/UI_TAG_OUTPUTS")

        return thisnode


# 必须存在
EXPORT_NODE = FilePathList

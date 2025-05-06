from typing import List, Dict, Optional, TYPE_CHECKING, Any, Union
import os
import io
import base64
import json
import glob
import fnmatch
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


FileImagePatterns = [
    "*.jpg",
    "*.jpeg",
    "*.png",
    "*.gif",
    "*.bmp",
    "*.webp",
    "*.tiff",
]
FileVideoPatterns = [
    "*.mp4",
    "*.avi",
    "*.mov",
    "*.wmv",
    "*.flv",
    "*.mkv",
    "*.webm",
]


class FilePathList(FATaskNode):
    def __init__(self, wid: str, nodeinfo: VFNodeInfo, runner: "FARunner"):
        super().__init__(wid, nodeinfo, runner)
        pass

    async def validate(self, validator: "FAValidator") -> Optional[ValidationError]:
        error_msgs = []
        try:
            node_payloads = self.data.Payloads
            D_FILE_PATH_LIST: VFNodeContentData = node_payloads.ById["D_FILE_PATH_LIST"]
            D_FILE_PATH_LIST_DATA = FilePathListData.model_validate(
                D_FILE_PATH_LIST.Data.value
            )
            if D_FILE_PATH_LIST_DATA.Type == FilePathListType.DIR:
                if not D_FILE_PATH_LIST_DATA.Dir:
                    error_msgs.append(f"目录不能为空")
                elif not os.path.exists(D_FILE_PATH_LIST_DATA.Dir):
                    error_msgs.append(f"目录不存在{D_FILE_PATH_LIST_DATA.Dir}")
                pass
            pass
        except Exception as e:
            errmsg = traceback.format_exc()
            error_msgs.append(f"获取内容失败{str(errmsg)}")

        if len(error_msgs) > 0:
            return ValidationError(nid=self.id, errors=error_msgs)
        return None

    def isMatch(
        self,
        file_name: str,
        pattern: str,
        quick_select: List[FilePathQuickSelect],
    ) -> bool:
        # 当pattern不存在且quick_select为空时，返回True
        if not pattern and not quick_select:
            return True

        # 优先检查pattern
        if pattern:
            return fnmatch.fnmatch(file_name, pattern)

        # 如果pattern不存在，检查quick_select
        if FilePathQuickSelect.IMAGE in quick_select:
            for img_pattern in FileImagePatterns:
                if fnmatch.fnmatch(file_name.lower(), img_pattern):
                    return True

        if FilePathQuickSelect.VIDEO in quick_select:
            for vid_pattern in FileVideoPatterns:
                if fnmatch.fnmatch(file_name.lower(), vid_pattern):
                    return True

        return False

    async def run(self) -> List[FANodeUpdateData]:
        node_payloads = self.data.Payloads
        D_FILE_PATH_LIST: VFNodeContentData = node_payloads.ById["D_FILE_PATH_LIST"]
        D_FILE_PATH_LIST_DATA = FilePathListData.model_validate(
            D_FILE_PATH_LIST.Data.value
        )

        if D_FILE_PATH_LIST_DATA.Type == FilePathListType.DIR:
            file_paths = []
            for root, dirs, files in os.walk(D_FILE_PATH_LIST_DATA.Dir):
                for file in files:
                    if self.isMatch(
                        file,
                        D_FILE_PATH_LIST_DATA.FileName,
                        D_FILE_PATH_LIST_DATA.QuickSelect,
                    ):
                        file_paths.append(os.path.join(root, file))
                if not D_FILE_PATH_LIST_DATA.Recursive:
                    break
                pass
            self.data.Results.ById["R_PATHS"].Data.value = [
                os.path.realpath(p) for p in file_paths
            ]
            pass
        elif D_FILE_PATH_LIST_DATA.Type == FilePathListType.REGEX:
            # 使用glob
            file_paths = glob.glob(
                D_FILE_PATH_LIST_DATA.Regex,
                recursive=D_FILE_PATH_LIST_DATA.Recursive,
            )
            self.data.Results.ById["R_PATHS"].Data.value = [
                os.path.realpath(p) for p in file_paths
            ]
            pass
        pass
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

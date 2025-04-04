from typing import List, Dict, Optional, TYPE_CHECKING, Any, Union, Literal
import asyncio
import os
import re
import ast
import copy
import sys
import json
import traceback
import base64
from loguru import logger
from enum import StrEnum
from pydantic import BaseModel
from app.schemas.VFNodeClass import VFNode
from app.schemas.vfnode import VFNodeInfo
from app.schemas.fanode import FARunStatus
from app.schemas.farequest import (
    ValidationError,
    FANodeUpdateType,
    FANodeUpdateData,
)
from app.schemas.vfnode_contentdata import VarType
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
    VFNodeHandleDataANode,
)
from app.utils.tools import read_yaml, reduceGet
from app.utils.db4node import loadNodeConfig, setNodeConfig


if TYPE_CHECKING:
    from app.services.FARunner import FARunner
    from app.services.FAValidator import FAValidator


THIS_NODE_NAME = "@FACodeInterpreter"


async def init_node_class():
    pass


class IterRun(FATaskNode):
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
        pass

    @staticmethod
    def getNodeCreateInfo():
        thisnode = VFNode("basenode")
        thisnode.set_flag(VFNodeFlag.IsTask | VFNodeFlag.IsNested)
        thisnode.init_as_nested_node("ITERRUN")
        thisnode.set_size(200, 200)

        thisnode.add_handle(VFNodeConnectionType.Inputs, "input", "Input")
        thisnode.add_handle(VFNodeConnectionType.Outputs, "output", "Output")
        thisnode.add_handle(VFNodeConnectionType.Self, "self")
        thisnode.add_handle(VFNodeConnectionType.Self, "attach_output")
        thisnode.add_handle(VFNodeConnectionType.Attach, "Attach")

        thisnode.add_attached_node("input", "@/FlowABuiltin/attach_node_input")
        thisnode.add_attached_node("output", "@/FlowABuiltin/attach_node_output")
        thisnode.add_attached_node("next", "@/FlowABuiltin/attach_node_next")

        thisnode.add_handle_data(
            VFNodeConnectionType.Self,
            "self",
            VFNodeHandleData(
                Type=VFNodeConnectionDataType.FromOuter,
                HandleId="input",
            ),
        )
        thisnode.add_handle_data(
            VFNodeConnectionType.Self,
            "attach_output",
            VFNodeHandleData(
                Type=VFNodeConnectionDataType.FromAttached,
                ANode={
                    "output": VFNodeHandleDataANode(
                        ConnectionType=VFNodeConnectionType.Self,
                        HandleId="self",
                    )
                },
            ),
        )

        # 只用于UI展示，没有实际作用
        thisnode.add_payload(
            VFNodeContentData(
                Label="",
                Type="List",
                Data=None,
                UiType="@/FlowABuiltin/UI_ITER_RUN_INNER_VAR",
            ),
        )

        # 这两个，删掉UiType就不会出现在UI上了，全部由上边的来展示
        pid_D_ITER_ITEM = thisnode.add_payload(
            VFNodeContentData(
                Label="迭代项目",
                Type="Any",
                Data=None,
            ),
            payload_id="D_ITER_ITEM",
        )
        pid_D_ITER_INDEX = thisnode.add_payload(
            VFNodeContentData(
                Label="迭代索引",
                Type="Integer",
                Data=None,
            ),
            payload_id="D_ITER_INDEX",
        )
        thisnode.add_handle_data(
            VFNodeConnectionType.Attach,
            "Attach",
            VFNodeHandleData(
                Type=VFNodeConnectionDataType.FromInner,
                Path=["Payloads", "ById", pid_D_ITER_ITEM],
            ),
        )
        thisnode.add_handle_data(
            VFNodeConnectionType.Attach,
            "Attach",
            VFNodeHandleData(
                Type=VFNodeConnectionDataType.FromInner,
                Path=["Payloads", "ById", pid_D_ITER_INDEX],
            ),
        )

        thisnode.add_payload(
            VFNodeContentData(
                Label="迭代数组",
                Type="String",
                Data='',
                UiType="@/FlowABuiltin/UI_ITER_RUN_ITER_ARRAY",
            ),
            payload_id="D_ITER_ARRAY",
        )

        thisnode.add_handle_data(
            VFNodeConnectionType.Attach,
            "Attach",
            VFNodeHandleData(
                Type=VFNodeConnectionDataType.FromOuter,
                HandleId="input",
            ),
        )

        thisnode.set_outputs_ui_type("@/FlowABuiltin/UI_ITER_RUN_OUTPUT")
        return thisnode


# 必须存在
EXPORT_NODE = IterRun
# 可选存在
EXPORT_INIT = init_node_class

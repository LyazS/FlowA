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
from app.schemas.VFNodeClass import VFNode
from app.schemas.VFNodeInterface import (
    VFNodeConnectionType,
    VFNodeFlag,
    VFNodeContentData,
    VFNodeHandleData,
    VFNodeConnectionDataType,
    VFNodeContentDataConfig,
    FromInnerPath,
)
from app.utils.tools import read_yaml, reduceGet, getUuid
from app.utils.db4node import loadNodeConfig, setNodeConfig
from app.services.FARunner import FARunner
from app.services.FAValidator import FAValidator
from ..UI_Components.UI_InputVars import InputVarModel, VarType


class NodeAndOutHandle(BaseModel):
    Node: str
    Handle: str
    pass


class Single_AggregateBranch(BaseModel):
    Node: str
    RefData: str
    OrderKey: ReadOnlyPropVar | str
    pass


class AggregateBranch(FATaskNode):
    def __init__(self, wid: str, nodeinfo: VFNodeInfo, runner: "FARunner"):
        super().__init__(wid, nodeinfo, runner)
        pass

    async def validate(self, validator: "FAValidator") -> Optional[ValidationError]:
        error_msgs = []
        try:
            node_payloads = self.data.Payloads
            node_results = self.data.Results

            selfVars = await validator.getConnectionByPath(
                self.id,
                [
                    CONNECT_DATA_TO_SELECT,
                    VFNodeConnectionType.Self,
                    "self",
                ],
            )

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
        thisnode.set_flag(VFNodeFlag.IsTask)
        thisnode.set_size(80, 80)
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
                Label="聚合分支变量",
                Type="List",
                Data=[
                    Single_AggregateBranch(
                        Node=NodeAndOutHandle(Node="", Handle="").model_dump_json(),
                        RefData="",
                        OrderKey=getUuid(),
                    ),
                ],
                UiType="@/FlowABuiltin/UI_AGGREGATE_BRANCH",
            ),
            payload_id="D_AGGREGATE_BRANCH",
        )

        thisnode.add_result_into_outputs(
            VFNodeContentData(
                Label="输出变量",
                Type="Any",
                Data=None,
            ),
            handle_id="output",
            result_id="D_OUTPUT",
        )

        thisnode.set_outputs_ui_type("@/FlowABuiltin/UI_TAG_OUTPUTS")
        return thisnode


# 必须存在
EXPORT_NODE = AggregateBranch

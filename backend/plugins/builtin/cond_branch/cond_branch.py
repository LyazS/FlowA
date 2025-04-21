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
from app.utils.tools import read_yaml, reduceGet
from app.utils.db4node import loadNodeConfig, setNodeConfig
from app.services.FARunner import FARunner
from app.services.FAValidator import FAValidator
from ..UI_Components.UI_InputVars import InputVarModel, VarType

LengthTypeSelections = [
    SelectOptions(label="长度等于", value="len_eq"),
    SelectOptions(label="长度不等于", value="len_ne"),
    SelectOptions(label="长度大于", value="len_gt"),
    SelectOptions(label="长度大于等于", value="len_gte"),
    SelectOptions(label="长度小于", value="len_lt"),
    SelectOptions(label="长度小于等于", value="len_lte"),
]
StartEndTypeSelections = [
    SelectOptions(label="开头是", value="startwith"),
    SelectOptions(label="结尾是", value="endwith"),
]
NullTypeSelections = [
    SelectOptions(label="为空", value="isnull"),
    SelectOptions(label="不为空", value="notnull"),
]
EqualTypeSelections = [
    SelectOptions(label="等于", value="eq"),
    SelectOptions(label="不等于", value="neq"),
]
NotEqualTypeSelections = [
    SelectOptions(label="大于", value="gt"),
    SelectOptions(label="大于等于", value="gte"),
    SelectOptions(label="小于", value="lt"),
    SelectOptions(label="小于等于", value="lte"),
]
ContainsTypeSelections = [
    SelectOptions(label="包含", value="contains"),
    SelectOptions(label="不包含", value="notcontains"),
]


class Single_Condition(BaseModel):
    Refdata: Optional[dict] = None
    Operator: str = "eq"
    CompareType: VarType = VarType.Ref
    ValueRef: Optional[dict] = None
    ValueStr: str = ""
    ValueNum: int | float = 0
    ValueBool: bool = False
    pass


class Single_ConditionDict(BaseModel):
    OutputKey: ReadOnlyPropVar | str
    CondIsAnd: bool
    Conditions: List[Single_Condition]
    pass


class CondBranch(FATaskNode):
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
        thisnode.add_handle(VFNodeConnectionType.Inputs, "input-cond", "CONDITION")
        thisnode.add_handle(VFNodeConnectionType.Inputs, "input-var", "VARIABLE")
        thisnode.add_handle(VFNodeConnectionType.Self, "self")
        thisnode.add_handle_data(
            VFNodeConnectionType.Self,
            "self",
            VFNodeHandleData(
                Type=VFNodeConnectionDataType.FromOuter,
                HandleId="input-cond",
            ),
        )

        thisnode.add_handle(VFNodeConnectionType.Outputs, "output-init", "CASE 1")
        thisnode.add_handle_data(
            VFNodeConnectionType.Outputs,
            "output-init",
            VFNodeHandleData(
                Type=VFNodeConnectionDataType.FromOuter,
                HandleId="input-var",
            ),
        )
        thisnode.add_result_into_outputs(
            VFNodeContentData(
                Label="CASE 1",
                Type="Dict",
                Data=Single_ConditionDict(
                    OutputKey="output-init",
                    CondIsAnd=True,
                    Conditions=[Single_Condition()],
                ),
            ),
            handle_id="output-init",
            result_id="output-init",
        )

        thisnode.add_handle(VFNodeConnectionType.Outputs, "output-else", "ELSE")
        thisnode.add_handle_data(
            VFNodeConnectionType.Outputs,
            "output-else",
            VFNodeHandleData(
                Type=VFNodeConnectionDataType.FromOuter,
                HandleId="input-var",
            ),
        )

        thisnode.set_outputs_ui_type("@/FlowABuiltin/UI_COND_BRANCH")
        return thisnode


# 必须存在
EXPORT_NODE = CondBranch

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
from app.schemas.VFlowRunData import FARunStatus, FANodeWaitType
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
    RefNodeHandleItem,
    RefVarItem,
)
from app.utils.tools import read_yaml, reduceGet, getUuid
from app.utils.db4node import loadNodeConfig, setNodeConfig
from app.services.FARunner import FARunner
from app.services.FAValidator import FAValidator
from ..UI_Components.UI_InputVars import InputVarModel, VarType


class Single_AggregateBranch(BaseModel):
    NodeHandle: Optional[RefNodeHandleItem] = None
    RefData: Optional[RefVarItem] = None
    OrderKey: ReadOnlyPropVar | str
    pass


class AggregateBranch(FATaskNode):
    def __init__(self, wid: str, nodeinfo: VFNodeInfo, runner: "FARunner"):
        super().__init__(wid, nodeinfo, runner)
        self.waitType = FANodeWaitType.OR
        pass

    async def validate(self, validator: "FAValidator") -> Optional[ValidationError]:
        error_msgs = []
        try:
            node_payloads = self.data.Payloads
            prehandles: List[RefNodeHandleItem] = await validator.getConnectionsByArgs(
                self.id,
                [
                    CONNECT_DATA,
                    "--node",
                    CONNECT_PRE_NODE,
                    "--inhid",
                    "input",
                    "--handle",
                    VFNodeConnectionType.Outputs,
                    "--stricthid",
                    "input",
                    "--outfmt",
                    CONNECT_DATA_TO_SELECT,
                    "--level",
                    CONNECT_HANDLE_LEVEL,
                ],
            )
            prehandles_set = set([ph.model_dump_json() for ph in prehandles])
            D_AGGREGATE_BRANCH: VFNodeContentData = node_payloads.ById[
                "D_AGGREGATE_BRANCH"
            ]
            aggBranchs: List[Single_AggregateBranch] = [
                Single_AggregateBranch.model_validate(data)
                for data in D_AGGREGATE_BRANCH.Data.value
            ]
            for branch in aggBranchs:
                if branch.NodeHandle is None:
                    error_msgs.append(f"缺少节点句柄")
                    continue
                else:
                    if branch.NodeHandle.model_dump_json() not in prehandles_set:
                        error_msgs.append(f"未定义前置节点句柄{branch.NodeHandle}")
                    pass
                if branch.RefData is None:
                    error_msgs.append(f"缺少变量")
                    continue
                else:
                    prevars: List[RefVarItem] = await validator.getConnectionsByArgs(
                        self.id,
                        [
                            CONNECT_DATA,
                            "--node",
                            branch.NodeHandle.Node,
                            "--inhid",
                            "input",
                            "--handle",
                            branch.NodeHandle.HandleType,
                            "--hid",
                            branch.NodeHandle.Handle,
                            "--outfmt",
                            CONNECT_DATA_TO_SELECT,
                            "--level",
                            CONNECT_VAR_LEVEL,
                        ],
                    )
                    prevars_set = set([pv.model_dump_json() for pv in prevars])
                    if branch.RefData.model_dump_json() not in prevars_set:
                        error_msgs.append(f"未定义变量{branch.RefData}")
                    pass
                pass

        except Exception as e:
            errmsg = traceback.format_exc()
            error_msgs.append(f"获取内容失败{str(errmsg)}")

        if len(error_msgs) > 0:
            return ValidationError(nid=self.id, errors=error_msgs)
        return None

    async def run(self) -> List[FANodeUpdateData]:
        try:
            node_payloads = self.data.Payloads

            D_AGGREGATE_BRANCH: VFNodeContentData = node_payloads.ById[
                "D_AGGREGATE_BRANCH"
            ]
            aggBranchs: List[Single_AggregateBranch] = [
                Single_AggregateBranch.model_validate(data)
                for data in D_AGGREGATE_BRANCH.Data.value
            ]
            for branch in aggBranchs:
                thenode: FATaskNode = self.runner().getNode(branch.NodeHandle.Node)
                owstatus = thenode.outputStatus[branch.NodeHandle.Handle]
                if owstatus == FARunStatus.Success:
                    refdata = await self.runner().getRefData(self.id, branch.RefData)
                    self.data.Results.ById["D_OUTPUT"].Data.value = refdata
                    break
                pass
            self.setAllOutputStatus(FARunStatus.Success)
            return []

        except Exception as e:
            errmsg = traceback.format_exc()
            raise Exception(f"聚合节点运行失败: {errmsg}")

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
                    Single_AggregateBranch(OrderKey=getUuid()),
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

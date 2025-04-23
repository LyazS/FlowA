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
    RefVarItem,
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
    Refdata: Optional[RefVarItem] = None
    Operator: str = "eq"
    CompareType: VarType = VarType.Ref
    ValueRef: Optional[RefVarItem] = None
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
            node_results = self.data.Results

            selfVars = await validator.getConnectionByPath(
                self.id,
                [
                    CONNECT_DATA_TO_SELECT,
                    VFNodeConnectionType.Self,
                    "self",
                ],
            )
            for rid in node_results.Order:
                item: VFNodeContentData = node_results.ById[rid]
                scd = None
                try:
                    scd = Single_ConditionDict.model_validate(item.Data.value)
                except:
                    error_msgs.append(f"条件配置错误{item.Data.value}")
                    continue
                brandname = item.Label
                for condition in scd.Conditions:
                    if (
                        not condition.Refdata
                        or condition.Refdata.model_dump_json() not in selfVars
                    ):
                        error_msgs.append(
                            f"分支{brandname} 对比变量未定义{condition.Refdata}"
                        )
                    if condition.CompareType == VarType.Ref and (
                        not condition.ValueRef
                        or condition.ValueRef.model_dump_json() not in selfVars
                    ):
                        error_msgs.append(
                            f"分支{brandname} 被对比变量未定义{condition.ValueRef}"
                        )

        except Exception as e:
            errmsg = traceback.format_exc()
            error_msgs.append(f"获取内容失败{str(errmsg)}")

        if len(error_msgs) > 0:
            return ValidationError(nid=self.id, errors=error_msgs)
        return None

    def compare(self, refdata, operator:str, compdata):
        # 基本比较操作符，适用于大多数可比较类型
        if operator == "eq":
            return refdata == compdata
        elif operator == "neq":
            return refdata != compdata

        # 数值比较操作符，需要确保两边都是可比较的数值类型
        elif operator in ["gt", "gte", "lt", "lte"]:
            try:
                if operator == "gt":
                    return refdata > compdata
                elif operator == "gte":
                    return refdata >= compdata
                elif operator == "lt":
                    return refdata < compdata
                elif operator == "lte":
                    return refdata <= compdata
            except TypeError:
                # 类型不兼容，无法比较
                return False

        # 字符串特定操作符
        elif operator in ["startwith", "endwith"]:
            if not isinstance(refdata, str):
                return False
            if not isinstance(compdata, str):
                try:
                    compdata = str(compdata)
                except:
                    return False

            if operator == "startwith":
                return refdata.startswith(compdata)
            elif operator == "endwith":
                return refdata.endswith(compdata)

        # 包含关系操作符
        elif operator in ["contains", "notcontains"]:
            try:
                if operator == "contains":
                    return compdata in refdata
                elif operator == "notcontains":
                    return compdata not in refdata
            except TypeError:
                # 类型不兼容，无法检查包含关系
                return False

        # 空值检查操作符
        elif operator == "isnull":
            return refdata is None
        elif operator == "notnull":
            return refdata is not None

        # 长度相关操作符，需要确保refdata是可计算长度的类型
        elif operator.startswith("len_"):
            try:
                refdata_len = len(refdata)
                if operator == "len_eq":
                    return refdata_len == compdata
                elif operator == "len_ne":
                    return refdata_len != compdata
                elif operator == "len_gt":
                    return refdata_len > compdata
                elif operator == "len_gte":
                    return refdata_len >= compdata
                elif operator == "len_lt":
                    return refdata_len < compdata
                elif operator == "len_lte":
                    return refdata_len <= compdata
            except (TypeError, AttributeError):
                # refdata不支持len()操作或比较类型不兼容
                return False

        # 未知操作符或不支持的类型组合
        return False

    async def run(self) -> List[FANodeUpdateData]:
        isAnyConditionMet = False
        node_results = self.data.Results
        for rid in node_results.Order:
            item: VFNodeContentData = node_results.ById[rid]
            idata = Single_ConditionDict.model_validate(item.Data.value)
            iOutputKey = idata.OutputKey
            conditionFunc = all if idata.CondIsAnd else any
            iconditions = idata.Conditions
            isConditionMet = []
            for condition in iconditions:
                refdata = await self.runner().getRefData(self.id, condition.Refdata)
                compdata = None
                if condition.CompareType == VarType.Ref:
                    compdata = await self.runner().getRefData(
                        self.id, condition.ValueRef
                    )
                elif condition.CompareType == VarType.String:
                    compdata = condition.ValueStr
                elif (
                    condition.CompareType == VarType.Number
                    or condition.CompareType == VarType.Integer
                ):
                    compdata = condition.ValueNum
                elif condition.CompareType == VarType.Boolean:
                    compdata = condition.ValueBool
                isConditionMet.append(
                    self.compare(refdata, condition.Operator, compdata)
                )
            if conditionFunc(isConditionMet):
                isAnyConditionMet = True
                self.setAllOutputStatus(FARunStatus.Canceled)
                self.setOutputStatus(iOutputKey, FARunStatus.Success)
                break
        if not isAnyConditionMet:
            self.setAllOutputStatus(FARunStatus.Canceled)
            self.setOutputStatus("output-else", FARunStatus.Success)
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
        thisnode.add_result(
            VFNodeContentData(
                Label="CASE 1",
                Type="Dict",
                Data=Single_ConditionDict(
                    OutputKey="output-init",
                    CondIsAnd=True,
                    Conditions=[Single_Condition()],
                ),
            ),
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

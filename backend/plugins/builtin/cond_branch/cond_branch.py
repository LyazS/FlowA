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


class ConditionType(StrEnum):
    AND = "AND"
    OR = "OR"
    pass


class Single_Condition(BaseModel):
    refdata: str
    operator: str
    comparetype: VarType
    valueStr: str
    valueNum: int | float
    valueBool: bool
    pass


class Single_ConditionDict(BaseModel):
    outputKey: ReadOnlyPropVar
    condType: ConditionType
    conditions: List[Single_Condition]
    pass


class CondBranch(FATaskNode):
    def __init__(self, wid: str, nodeinfo: VFNodeInfo, runner: "FARunner"):
        super().__init__(wid, nodeinfo, runner)
        pass

    async def validate(self, validator: "FAValidator") -> Optional[ValidationError]:
        error_msgs = []
        try:
            # 首先要检查输入
            # 收集输出名字
            # 然后检查代码需求的输入是否在输入data里边
            # 然后检查输出data是否在输出data里边
            CodeInputArgs = set()
            CodeOutputArgs = []
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

            D_INPUT_VARS: VFNodeContentData = node_payloads.ById["D_INPUT_VARS"]
            for var_dict in D_INPUT_VARS.Data.value:
                var = InputVarModel.model_validate(var_dict)
                if var.type == VarType.Ref and var.valueStr not in selfVars:
                    error_msgs.append(f"没有该变量选项{var.valueStr}")
                else:
                    CodeInputArgs.add(var.key)
            for pid in node_results.Order:
                item: VFNodeContentData = node_results.ById[pid]
                CodeOutputArgs.append(item.Label)
                pass

            D_CODE: VFNodeContentData = node_payloads.ById["D_CODE"]
            if not isinstance(D_CODE.Data.value, str):
                raise Exception(f"Python代码格式错误")
            try:
                tree = ast.parse(D_CODE.Data.value)
                hasMain = False
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name == "main":
                        hasMain = True
                        # 检查输入名字是否对上
                        input_params = [arg.arg for arg in node.args.args]
                        for in_arg in input_params:
                            if in_arg not in CodeInputArgs:
                                error_msgs.append(f"缺少输入参数【{in_arg}】")
                            pass
                        # 检查输出名字是否对上
                        return_statements = [
                            n for n in ast.walk(node) if isinstance(n, ast.Return)
                        ]
                        for return_node in return_statements:
                            if isinstance(return_node.value, ast.Dict):
                                outputs = set([key.s for key in return_node.value.keys])
                                for out_arg in CodeOutputArgs:
                                    if out_arg not in outputs:
                                        error_msgs.append(
                                            f"代码返回值缺少输出参数【{out_arg}】"
                                        )
                                    pass
                            else:
                                error_msgs.append(f"main函数返回值必须为字典")
                            pass
                        break
                if not hasMain:
                    error_msgs.append(f"未找到main函数")
            except SyntaxError:
                error_msgs.append(f"Python代码格式错误")
            except Exception as e:
                error_msgs.append(str(e))

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
        thisnode.add_handle(VFNodeConnectionType.Outputs, "output-else", "ELSE")
        thisnode.add_handle(VFNodeConnectionType.Self, "self")
        thisnode.add_handle_data(
            VFNodeConnectionType.Self,
            "self",
            VFNodeHandleData(
                Type=VFNodeConnectionDataType.FromOuter,
                HandleId="input-cond",
            ),
        )
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

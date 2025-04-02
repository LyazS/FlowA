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
from enum import StrEnum
from pydantic import BaseModel
from app.schemas.VFNodeClass import VFNode
from app.schemas.vfnode import VFNodeInfo
from app.schemas.fanode import FANodeValidateNeed
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
)
from app.utils.tools import read_yaml
from app.utils.db4node import loadNodeConfig, setNodeConfig

if TYPE_CHECKING:
    from app.services.FARunner import FARunner
    from app.services.FAValidator import FAValidator

from ..UI_Components.UI_InputVars import DefaultInputVar


class EvalType(StrEnum):
    Python = "Python"
    SnekBox = "SnekBox"
    pass


class CodeOutput(BaseModel):
    success: bool
    output: Union[Dict, str] = None
    error: str = None
    pass


THIS_NODE_NAME = "@FACodeInterpreter"
NodeConfig = {}
CODE_TEMPLATE_FUNCTION = None
CODE_TEMPLATE_INPUT = None
CODE_TEMPLATE_OUTPUT_RE = None
CODE_TEMPLATE = None
EVALTYPE = None
SNEKBOXURL = None


async def init_node_class():
    global NodeConfig
    global CODE_TEMPLATE_FUNCTION
    global CODE_TEMPLATE_INPUT
    global CODE_TEMPLATE_OUTPUT_RE
    global CODE_TEMPLATE
    global EVALTYPE
    global SNEKBOXURL
    ret, config = await loadNodeConfig(THIS_NODE_NAME)
    if ret:
        NodeConfig = config
    else:
        NodeConfig = read_yaml(
            os.path.join(
                os.path.dirname(__file__),
                "FANode_code_interpreter.yaml",
            )
        )
        await setNodeConfig(THIS_NODE_NAME, NodeConfig)
    CODE_TEMPLATE_FUNCTION = NodeConfig["codetemplate_func"]
    CODE_TEMPLATE_INPUT = NodeConfig["codetemplate_input"]
    CODE_TEMPLATE_OUTPUT_RE = NodeConfig["codetemplate_output_re"]
    CODE_TEMPLATE = NodeConfig["codetemplate"]

    EVALTYPE = EvalType(NodeConfig["evaltype"])
    SNEKBOXURL = NodeConfig.get("snekboxUrl", "")

    pass


async def SimplePythonRun(code, evaltype: EvalType, snekboxUrl: str = ""):
    if evaltype == EvalType.Python:
        python_executable = sys.executable

        # Use asyncio.create_subprocess_exec for async subprocess handling
        process = await asyncio.create_subprocess_exec(
            python_executable,
            "-Xfrozen_modules=off",
            "-c",
            code,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        # Wait for the process to complete and capture output
        stdout_b, stderr_b = await process.communicate()
        stdout = stdout_b.decode("utf-8").replace("\r", "")
        stderr = stderr_b.decode("utf-8").replace("\r", "")
        if len(stdout) <= 0:
            raise Exception("代码格式问题:\n", stderr)

        output_result = re.findall(CODE_TEMPLATE_OUTPUT_RE, stdout, re.S)

        if len(output_result) > 0:
            output_type, res = output_result[-1].strip().split("\n", 1)
            if "@CODEOUTPUT-BASE64" in output_type:
                json_string = base64.b64decode(res).decode("utf-8")
                res_json = json.loads(json_string)
                return CodeOutput(success=True, output=res_json)
            elif "@CODEOUTPUT-ERROR" in output_type:
                return CodeOutput(success=False, error=res)
            else:
                return CodeOutput(success=False, error="代码执行失败，请检查代码输出")

    elif evaltype == EvalType.SnekBox:
        raise Exception(f"不支持的执行类型{evaltype}")
    else:
        raise Exception(f"不支持的执行类型{evaltype}")


class CodeInterpreter(FATaskNode):
    def __init__(self, wid: str, nodeinfo: VFNodeInfo, runner: "FARunner"):
        super().__init__(wid, nodeinfo, runner)
        pass

    def validate(self, validator: "FAValidator") -> Optional[ValidationError]:
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

            D_INPUT_VARS: VFNodeContentData = node_payloads.ById["D_INPUT_VARS"]
            for var_dict in D_INPUT_VARS.Data.value:
                var = Single_VarInput.model_validate(var_dict)
                if var.type == VarType.Ref and var.value not in selfVars:
                    error_msgs.append(f"没有该变量选项{var.value}")
                else:
                    CodeInputArgs.add(var.key)
            for pid in node_results.order:
                item: VFNodeContentData = node_results.byId[pid]
                CodeOutputArgs.append(item.key)
                pass

            D_CODE: VFNodeContentData = node_payloads.byId["D_CODE"]
            if not isinstance(D_CODE.data.value, str):
                raise Exception(f"Python代码格式错误")
            try:
                tree = ast.parse(D_CODE.data.value)
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

    @staticmethod
    def getNodeConfig():
        return {}

    @staticmethod
    def getNodeCreateInfo():
        thisnode = VFNode("basenode")
        thisnode.set_flag(VFNodeFlag.IsTask)
        thisnode.set_size(80, 80)
        thisnode.add_handle(VFNodeConnectionType.Inputs, "input", "Input")
        thisnode.add_handle(VFNodeConnectionType.Outputs, "output", "Output")
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
                Label="输入变量",
                Type="List",
                Data=[
                    DefaultInputVar(key="arg1", valueStr="hello"),
                    DefaultInputVar(key="arg2", valueStr="world"),
                ],
                UiType="@/FlowABuiltin/UI_INPUT_VARS",
            ),
            payload_id="D_INPUT_VARS",
        )
        thisnode.add_payload(
            VFNodeContentData(
                Label="Python代码",
                Type="String",
                Data='#You can use numpy and cv2 by import\ndef main(arg1, arg2):\n    # do something\n    return {\n        "output1": arg1,\n        "output2": arg2\n    }',
                UiType="@/FlowABuiltin/UI_CODE_EDITOR",
                Config=VFNodeContentDataConfig(Language="python"),
            ),
            payload_id="D_CODE",
        )

        thisnode.add_result_into_outputs(
            VFNodeContentData(
                Label="output1",
                Type="String",
                Data="",
            ),
            handle_id="output",
        )
        thisnode.add_result_into_outputs(
            VFNodeContentData(
                Label="output2",
                Type="String",
                Data="",
            ),
            handle_id="output",
        )
        thisnode.set_outputs_ui_type("@/FlowABuiltin/UI_CODE_OUTPUT")
        return thisnode


# 必须存在
EXPORT_NODE = CodeInterpreter
# 可选存在
EXPORT_INIT = init_node_class

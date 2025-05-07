from typing import List, Dict, Optional, TYPE_CHECKING, Any, Union, Literal
import asyncio
import os
import ast
import copy
import sys
import traceback
import dill  # 使用dill代替pickle
from loguru import logger
from enum import StrEnum
from pydantic import BaseModel
from app.schemas.VFNodeClass import VFNode
from app.schemas.VFlowData import VFNodeInfo
from app.schemas.VFlowRunData import FARunStatus
from app.schemas.farequest import (
    ValidationError,
    FANodeUpdateData,
)
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
from app.services.FARunner import FARunner
from app.services.FAValidator import FAValidator
from app.utils.vueRef import pickle_ref
from ..UI_Components.UI_InputVars import InputVarModel, VarType


class EvalType(StrEnum):
    Python = "Python"
    SnekBox = "SnekBox"
    pass


class CodeOutput(BaseModel):
    success: bool
    output: Union[Dict, str, bytes] = None
    error: str = None
    pass


THIS_NODE_NAME = "@FACodeInterpreter"
NODE_CONFIG = {}
CODE_TEMPLATE_FUNCTION = None
CODE_TEMPLATE = None
EVALTYPE = None


async def init_node_class():
    global NODE_CONFIG
    global CODE_TEMPLATE_FUNCTION
    global CODE_TEMPLATE
    global EVALTYPE

    # 检查并安装dill模块
    try:
        import dill
    except ImportError:
        logger.info("正在安装dill模块...")
        import subprocess

        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "dill"])
            logger.info("dill模块安装成功")
        except Exception as e:
            logger.error(f"安装dill模块失败: {str(e)}")

    ret, config = await loadNodeConfig(THIS_NODE_NAME)
    if ret:
        NODE_CONFIG = config
    else:
        NODE_CONFIG = read_yaml(
            os.path.join(
                os.path.dirname(__file__),
                "FANode_code_interpreter.yaml",
            )
        )
        await setNodeConfig(THIS_NODE_NAME, NODE_CONFIG)
    CODE_TEMPLATE_FUNCTION = NODE_CONFIG["codetemplate_func"]
    CODE_TEMPLATE = NODE_CONFIG["codetemplate"]

    EVALTYPE = EvalType(NODE_CONFIG["evaltype"])

    pass


async def SimplePythonRun(code, evaltype: EvalType, input_data=None, cancel_event=None):
    if evaltype == EvalType.Python:
        import tempfile
        import uuid

        # 创建临时目录用于数据交换
        temp_dir = tempfile.gettempdir()
        session_id = str(uuid.uuid4())
        input_file = os.path.join(temp_dir, f"code_input_{session_id}.dill")
        output_file = os.path.join(temp_dir, f"code_output_{session_id}.dill")

        process = None

        try:
            # 将输入数据保存到临时文件，使用dill代替pickle
            if input_data:
                with open(input_file, "wb") as f:
                    dill.dump(input_data, f)

            # 修改代码，添加临时文件路径和dill导入
            code_with_paths = f"""
# 添加临时文件路径
import dill  # 使用dill代替pickle
_CI_INPUT_FILE = "{input_file.replace('\\', '\\\\')}"
_CI_OUTPUT_FILE = "{output_file.replace('\\', '\\\\')}"

{code}
"""

            python_executable = sys.executable

            # Use asyncio.create_subprocess_exec for async subprocess handling
            process = await asyncio.create_subprocess_exec(
                python_executable,
                "-Xfrozen_modules=off",
                "-c",
                code_with_paths,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            # 创建一个任务来等待进程完成
            process_task = asyncio.create_task(process.communicate())

            # 如果提供了取消事件，则同时等待取消事件
            if cancel_event:
                cancel_task = asyncio.create_task(cancel_event.wait())
                done, pending = await asyncio.wait(
                    [process_task, cancel_task], return_when=asyncio.FIRST_COMPLETED
                )

                # 如果取消事件先完成，则终止进程
                if cancel_task in done:
                    logger.info("代码执行被取消")
                    if process.returncode is None:
                        try:
                            process.terminate()  # 尝试优雅终止
                            await asyncio.sleep(0.5)
                            if process.returncode is None:
                                process.kill()  # 如果还没结束，强制终止
                        except Exception as e:
                            logger.warning(f"终止进程失败: {str(e)}")

                    # 取消未完成的任务
                    for task in pending:
                        task.cancel()
                        try:
                            await task
                        except asyncio.CancelledError:
                            pass

                    raise asyncio.CancelledError("代码执行被取消")

                # 取消未完成的任务
                for task in pending:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass

                stdout_b, stderr_b = process_task.result()
            else:
                # 如果没有取消事件，直接等待进程完成
                stdout_b, stderr_b = await process_task

            stdout = stdout_b.decode("utf-8").replace("\r", "")
            stderr = stderr_b.decode("utf-8").replace("\r", "")

            # 检查是否有错误输出
            if stderr and not stdout:
                raise Exception(f"代码执行错误:\n{stderr}")

            # 检查输出文件是否存在
            if os.path.exists(output_file):
                try:
                    # 从输出文件读取结果，使用dill代替pickle
                    with open(output_file, "rb") as f:
                        result = dill.load(f)

                    # 检查结果是否包含错误信息
                    if (
                        isinstance(result, dict)
                        and "error" in result
                        and result.get("success") is False
                    ):
                        return CodeOutput(success=False, error=result["error"])

                    return CodeOutput(success=True, output=result)
                except Exception as e:
                    return CodeOutput(success=False, error=f"读取结果失败: {str(e)}")

            # 如果没有输出文件，可能是代码执行出错
            return CodeOutput(
                success=False, error=f"代码执行失败，无法获取结果: {stdout}\n{stderr}"
            )

        finally:
            # 无论如何都要清理临时文件
            try:
                if os.path.exists(input_file):
                    os.remove(input_file)
                if os.path.exists(output_file):
                    os.remove(output_file)
            except Exception as e:
                logger.warning(f"清理临时文件失败: {str(e)}")

            # 确保进程被终止
            if process and process.returncode is None:
                try:
                    process.terminate()
                    await asyncio.sleep(0.1)
                    if process.returncode is None:
                        process.kill()
                except Exception as e:
                    logger.warning(f"终止进程失败: {str(e)}")

    elif evaltype == EvalType.SnekBox:
        raise Exception(f"不支持的执行类型{evaltype}")
    else:
        raise Exception(f"不支持的执行类型{evaltype}")


class CodeInterpreter(FATaskNode):
    def __init__(self, wid: str, nodeinfo: VFNodeInfo, runner: "FARunner"):
        super().__init__(wid, nodeinfo, runner)
        # 用于取消代码执行的事件
        self.code_cancel_event = asyncio.Event()

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
                if var.Type == VarType.Ref and (
                    not var.ValueRef or var.ValueRef.model_dump_json() not in selfVars
                ):
                    error_msgs.append(f"没有该变量选项{var.ValueRef}")
                else:
                    CodeInputArgs.add(var.Key)
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
        """
        重写run方法，添加取消事件的处理
        """
        try:
            # 重置取消事件
            self.code_cancel_event.clear()

            # 执行原来的run逻辑
            CodeInputArgs = {}
            node_payloads = self.data.Payloads
            node_results = self.data.Results

            D_INPUT_VARS: VFNodeContentData = node_payloads.ById["D_INPUT_VARS"]
            for var_dict in D_INPUT_VARS.Data.value:
                var = InputVarModel.model_validate(var_dict)
                CodeInputArgs[var.Key] = await InputVarModel.get_value(
                    var,
                    self.id,
                    self.runner().getRefData,
                )
            D_CODE: VFNodeContentData = node_payloads.ById["D_CODE"]

            # 开始执行代码
            code_run: str = copy.deepcopy(CODE_TEMPLATE)
            code_run = code_run.replace(CODE_TEMPLATE_FUNCTION, D_CODE.Data.value)

            # 使用临时文件方式传递数据，并传递取消事件
            codeResult = await SimplePythonRun(
                code_run,
                EVALTYPE,
                input_data=CodeInputArgs,
                cancel_event=self.code_cancel_event,
            )

            if codeResult.success:
                for rid in node_results.Order:
                    item: VFNodeContentData = node_results.ById[rid]
                    if item.Label not in codeResult.output:
                        raise Exception(f"实际返回结果缺少输出参数【{item.Label}】")

                    # 更新内部数据
                    self.data.Results.ById[rid].Data.value = codeResult.output[
                        item.Label
                    ]

                # 返回之前要设置好输出handle状态
                self.setAllOutputStatus(FARunStatus.Success)
                return []
            else:
                raise Exception(f"执行代码失败：{codeResult.error}")
        except asyncio.CancelledError:
            # 节点被取消时，设置代码取消事件
            self.code_cancel_event.set()
            # 重新抛出异常，让父类处理
            raise
        except Exception as e:
            # 其他异常也设置取消事件，确保资源被释放
            self.code_cancel_event.set()
            # 重新抛出异常，让父类处理
            raise

    @staticmethod
    async def getNodeConfig():
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
                Type=VarType.List,
                Data=[
                    InputVarModel(Key="arg1", ValueStr="hello"),
                    InputVarModel(Key="arg2", ValueStr="world"),
                ],
                UiType="@/FlowABuiltin/UI_INPUT_VARS",
            ),
            payload_id="D_INPUT_VARS",
        )
        thisnode.add_payload(
            VFNodeContentData(
                Label="Python代码",
                Type=VarType.String,
                Data='#You can import some modules here\ndef main(arg1, arg2):\n    # do something\n    return {\n        "output1": arg1,\n        "output2": arg2\n    }',
                UiType="@/FlowABuiltin/UI_CODE_EDITOR",
                Config=VFNodeContentDataConfig(Language="python"),
            ),
            payload_id="D_CODE",
        )

        thisnode.add_result_into_outputs(
            VFNodeContentData(
                Label="output1",
                Type=VarType.String,
                Data="",
            ),
            handle_id="output",
        )
        thisnode.add_result_into_outputs(
            VFNodeContentData(
                Label="output2",
                Type=VarType.String,
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

import asyncio
from typing import Callable, Awaitable, Any, Dict, Optional
from pydantic import BaseModel
from loguru import logger
from .FARunner import FARunner


class TaskModel(BaseModel):
    runner: FARunner
    task: Optional[asyncio.Task] = None

    class Config:
        arbitrary_types_allowed = True

    pass


class TaskMgr:
    """
    设计规范：
    1. wid 存在即表示任务存在（无论是否完成）
    2. 需要显式调用 stop 才会移除任务
    3. 即使完成，用户人需要观察结果，所以不应该立即删除wid
    """

    def __init__(self):
        self.tasks: Dict[str, TaskModel] = {}
        self.lock = asyncio.Lock()

    async def isRunning(self, wid: str) -> bool:
        """检查是否在运行"""
        return wid in self.tasks

    async def start_run(self, wid: str, vflow_data: dict):
        """启动运行"""
        async with self.lock:
            # 防止重复创建
            if wid not in self.tasks:
                self.tasks[wid] = TaskModel(
                    runner=FARunner(wid, vflow_data),
                    task=None,
                )
                self.tasks[wid].task = asyncio.create_task(self.tasks[wid].runner.run())
            else:
                logger.warning(f"Task {wid} already exists, ignoring start request.")
        pass

    async def stop(self, wid: str):
        """停止命令"""
        async with self.lock:
            if wid in self.tasks:
                if task_model := self.tasks[wid].task:
                    task_model.cancel()
                    try:
                        await task_model  # 等待任务完全终止
                        logger.debug(f"Task {wid} cancelled successfully.")
                    except asyncio.CancelledError:
                        logger.error(f"Task {wid} cancelled in unexpected way.")
                        pass  # 预期内的取消异常
                    except Exception as e:
                        logger.error(f"Task {wid} failed: {e}")
                del self.tasks[wid]
            pass

    async def get(self, wid: str) -> Optional[FARunner]:
        """获取任务"""
        async with self.lock:
            if wid in self.tasks:
                return self.tasks[wid].runner
            else:
                return None
        pass

    # 获取所用正在运行的任务
    async def getAllTaskID(self):
        async with self.lock:
            return list(self.tasks.keys())
        pass


ALL_TASKS_MGR = TaskMgr()

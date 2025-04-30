from typing import Dict, List, Tuple, Optional, TYPE_CHECKING
import asyncio
from app.utils.logging import logger


# 全局缓存字典，格式: {wid: {nid: {cache_key: data}}}
_GLOBAL_CACHE: Dict[str, Dict[str, Dict[str, dict]]] = {}
# 全局锁，用于保护对全局缓存的访问
_GLOBAL_LOCK = asyncio.Lock()


class MemCacheMgr:
    def __init__(self, wid: str):
        self.wid = wid
        # 用于存储待提交的缓存操作
        # 格式: [(nid, cache_key, data), ...]
        self.pending_operations: List[Tuple[str, str, dict]] = []
        # 添加锁机制以确保线程安全
        self.lock = asyncio.Lock()

    async def set(
        self,
        nid: str,
        cache_key: str,
        data: dict,
        isCommit: bool = False,
    ):
        """
        将缓存保存到内存
        如果已有则覆盖

        当isCommit为True时，立即提交到内存缓存
        当isCommit为False时，将操作添加到待提交队列，需要稍后调用batchcommit提交
        """
        if isCommit:
            # 直接提交到全局内存缓存
            async with _GLOBAL_LOCK:
                # 确保wid和nid的字典存在
                if self.wid not in _GLOBAL_CACHE:
                    _GLOBAL_CACHE[self.wid] = {}
                if nid not in _GLOBAL_CACHE[self.wid]:
                    _GLOBAL_CACHE[self.wid][nid] = {}
                # 更新或创建缓存条目
                _GLOBAL_CACHE[self.wid][nid][cache_key] = data
                logger.debug(
                    f"Directly committed to global memory cache for wid {self.wid}: {nid}, {cache_key}"
                )
        else:
            # 添加到待提交队列，使用锁保护对共享数据的访问
            async with self.lock:
                self.pending_operations.append((nid, cache_key, data))
                logger.debug(
                    f"Added operation to pending queue for wid {self.wid}: {nid}, {cache_key}"
                )

    async def batchcommit(self):
        """
        批量提交待处理的缓存操作到全局内存缓存
        """
        # 使用锁保护对pending_operations的访问
        async with self.lock:
            if not self.pending_operations:
                logger.debug("No pending operations to commit")
                return

            logger.debug(
                f"Batch committing {len(self.pending_operations)} operations for wid {self.wid}"
            )

            # 复制要提交的操作，以便在锁外进行全局缓存操作
            operations_to_commit = self.pending_operations.copy()
            self.pending_operations.clear()

        # 锁外进行全局缓存操作，减少锁的持有时间
        async with _GLOBAL_LOCK:
            # 确保wid的字典存在
            if self.wid not in _GLOBAL_CACHE:
                _GLOBAL_CACHE[self.wid] = {}

            # 处理当前工作流的所有待提交操作
            for nid, cache_key, data in operations_to_commit:
                # 确保nid的字典存在
                if nid not in _GLOBAL_CACHE[self.wid]:
                    _GLOBAL_CACHE[self.wid][nid] = {}
                # 更新或创建缓存条目
                _GLOBAL_CACHE[self.wid][nid][cache_key] = data

            logger.debug(f"Batch commit completed for wid {self.wid}")

    async def get(self, nid: str, cache_key: str) -> Optional[dict]:
        """从全局内存缓存加载数据"""
        async with _GLOBAL_LOCK:
            # 检查wid是否存在于全局缓存中
            if self.wid not in _GLOBAL_CACHE:
                return None
            # 检查nid是否存在于wid的缓存中
            if nid not in _GLOBAL_CACHE[self.wid]:
                return None
            # 检查cache_key是否存在于nid的缓存中
            return _GLOBAL_CACHE[self.wid][nid].get(cache_key)

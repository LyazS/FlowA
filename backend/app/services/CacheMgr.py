from typing import Dict, List, Tuple, TYPE_CHECKING
import asyncio
from sqlalchemy import select
from app.db.session import get_db_ctxmgr
from app.models.fastore import FANodeCacheModel
from app.utils.logging import logger


class CacheMgr:
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
        将缓存保存到数据库
        如果已有则覆盖

        当isCommit为True时，立即提交到数据库
        当isCommit为False时，将操作添加到待提交队列，需要稍后调用batchcommit提交
        """
        if isCommit:
            # 直接提交到数据库
            async with get_db_ctxmgr() as session:
                # Check if the cache entry already exists
                result = await session.execute(
                    select(FANodeCacheModel).where(
                        FANodeCacheModel.key == cache_key,
                        FANodeCacheModel.wid == self.wid,
                        FANodeCacheModel.nid == nid,
                    )
                )
                cache_entry = result.scalar_one_or_none()

                if cache_entry:
                    # Update the existing entry
                    cache_entry.data = data
                else:
                    # Create a new entry
                    cache_entry = FANodeCacheModel(
                        key=cache_key,
                        data=data,
                        wid=self.wid,
                        nid=nid,
                    )
                    session.add(cache_entry)
                await session.commit()
        else:
            # 添加到待提交队列，使用锁保护对共享数据的访问
            async with self.lock:
                self.pending_operations.append((nid, cache_key, data))
                logger.debug(
                    f"Added operation to pending queue for wid {self.wid}: {nid}, {cache_key}"
                )

    async def batchcommit(self):
        """
        批量提交待处理的缓存操作
        """
        # 使用锁保护对pending_operations的访问
        async with self.lock:
            if not self.pending_operations:
                logger.debug("No pending operations to commit")
                return

            logger.debug(
                f"Batch committing {len(self.pending_operations)} operations for wid {self.wid}"
            )
            # 复制要提交的操作，以便在锁外进行数据库操作
            operations_to_commit = self.pending_operations.copy()
            self.pending_operations.clear()

        # 锁外进行数据库操作，减少锁的持有时间
        async with get_db_ctxmgr() as session:
            # 处理当前工作流的所有待提交操作
            for nid, cache_key, data in operations_to_commit:
                # 检查缓存条目是否已存在
                result = await session.execute(
                    select(FANodeCacheModel).where(
                        FANodeCacheModel.key == cache_key,
                        FANodeCacheModel.wid == self.wid,
                        FANodeCacheModel.nid == nid,
                    )
                )
                cache_entry = result.scalar_one_or_none()

                if cache_entry:
                    # 更新现有条目
                    cache_entry.data = data
                else:
                    # 创建新条目
                    cache_entry = FANodeCacheModel(
                        key=cache_key,
                        data=data,
                        wid=self.wid,
                        nid=nid,
                    )
                    session.add(cache_entry)

            # 一次性提交当前工作流的所有更改
            await session.commit()
            logger.debug(f"Batch commit completed for wid {self.wid}")
        pass

    async def get(self, nid: str, cache_key: str):
        """从数据库加载缓存"""
        async with get_db_ctxmgr() as session:
            result = await session.execute(
                select(FANodeCacheModel.data).where(
                    FANodeCacheModel.key == cache_key,
                    FANodeCacheModel.wid == self.wid,
                    FANodeCacheModel.nid == nid,
                )
            )
            cache_entry = result.scalar_one_or_none()
            return cache_entry if cache_entry else None

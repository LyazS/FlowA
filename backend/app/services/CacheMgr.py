from typing import Dict, List, Tuple
import asyncio

from app.db.session import get_db_ctxmgr
from app.models.fastore import FANodeCacheModel
from sqlalchemy import select
from app.utils.logging import logger


class CacheMgr:
    def __init__(self):
        # 用于存储待提交的缓存操作
        # 格式: {wid: [(nid, cache_key, data), ...], ...}
        # 使用wid作为键，可以针对特定工作流进行批量提交
        self.pending_operations: Dict[str, List[Tuple[str, str, dict]]] = {}
        # 添加锁机制以确保线程安全
        self.lock = asyncio.Lock()

    async def set(
        self,
        wid: str,
        nid: str,
        cache_key: str,
        data: dict,
        isCommit: bool = True,
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
                        FANodeCacheModel.wid == wid,
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
                        wid=wid,
                        nid=nid,
                    )
                    session.add(cache_entry)
                await session.commit()
        else:
            # 添加到待提交队列，使用锁保护对共享数据的访问
            async with self.lock:
                if wid not in self.pending_operations:
                    self.pending_operations[wid] = []
                self.pending_operations[wid].append((nid, cache_key, data))
                logger.debug(f"Added operation to pending queue for wid {wid}: {nid}, {cache_key}")

    async def batchcommit(self, wid: str = None):
        """
        批量提交待处理的缓存操作

        参数:
            wid: 工作流ID。如果指定，只提交该工作流的操作；如果为None，提交所有工作流的操作。
        """
        # 使用锁保护对pending_operations的访问
        async with self.lock:
            if not self.pending_operations:
                logger.debug("No pending operations to commit")
                return

            # 如果指定了wid，只提交该wid的操作
            if wid is not None:
                if wid not in self.pending_operations:
                    logger.debug(f"No pending operations for wid {wid}")
                    return
                wids_to_commit = [wid]
                total_ops = len(self.pending_operations[wid])
                logger.debug(f"Batch committing {total_ops} operations for wid {wid}")
            else:
                # 提交所有工作流的操作
                wids_to_commit = list(self.pending_operations.keys())
                total_ops = sum(len(ops) for ops in self.pending_operations.values())
                logger.debug(f"Batch committing {total_ops} operations for all workflows")

            # 复制要提交的操作，以便在锁外进行数据库操作
            operations_to_commit = {}
            for current_wid in wids_to_commit:
                operations_to_commit[current_wid] = self.pending_operations[current_wid].copy()

        # 锁外进行数据库操作，减少锁的持有时间
        for current_wid, operations in operations_to_commit.items():
            async with get_db_ctxmgr() as session:
                # 处理当前工作流的所有待提交操作
                for nid, cache_key, data in operations:
                    # 检查缓存条目是否已存在
                    result = await session.execute(
                        select(FANodeCacheModel).where(
                            FANodeCacheModel.key == cache_key,
                            FANodeCacheModel.wid == current_wid,
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
                            wid=current_wid,
                            nid=nid,
                        )
                        session.add(cache_entry)

                # 一次性提交当前工作流的所有更改
                await session.commit()
                logger.debug(f"Batch commit completed for wid {current_wid}")

                # 提交成功后，使用锁保护删除已提交的操作
                async with self.lock:
                    if current_wid in self.pending_operations:
                        del self.pending_operations[current_wid]

        logger.debug("Batch commit completed successfully")

    async def get(self, wid: str, nid: str, cache_key: str):
        """从数据库加载缓存"""
        async with get_db_ctxmgr() as session:
            result = await session.execute(
                select(FANodeCacheModel.data).where(
                    FANodeCacheModel.key == cache_key,
                    FANodeCacheModel.wid == wid,
                    FANodeCacheModel.nid == nid,
                )
            )
            cache_entry = result.scalar_one_or_none()
            return cache_entry if cache_entry else None


GOLBAL_CACHE_MGR = CacheMgr()

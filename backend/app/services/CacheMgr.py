from typing import Dict, List, TYPE_CHECKING, Set, Union

from app.db.session import get_db_ctxmgr
from app.models.fastore import FANodeCacheModel
from sqlalchemy import select


class CacheMgr:
    def __init__(self):
        pass

    async def set(self, wid: str, cache_key: str, data: dict):
        """
        将缓存保存到数据库
        如果已有则覆盖
        """
        async with get_db_ctxmgr() as session:
            # Check if the cache entry already exists
            result = await session.execute(
                select(FANodeCacheModel).where(
                    FANodeCacheModel.key == cache_key,
                    FANodeCacheModel.wid == wid,
                )
            )
            cache_entry = result.scalar_one_or_none()

            if cache_entry:
                # Update the existing entry
                cache_entry.data = data
            else:
                # Create a new entry
                cache_entry = FANodeCacheModel(key=cache_key, data=data, wid=wid)
                session.add(cache_entry)

            await session.commit()

    async def get(self, wid: str, cache_key: str):
        """从数据库加载缓存"""
        async with get_db_ctxmgr() as session:
            result = await session.execute(
                select(FANodeCacheModel.data).where(
                    FANodeCacheModel.key == cache_key,
                    FANodeCacheModel.wid == wid,
                )
            )
            cache_entry = result.scalar_one_or_none()
            return cache_entry if cache_entry else None


GOLBAL_CACHE_MGR = CacheMgr()

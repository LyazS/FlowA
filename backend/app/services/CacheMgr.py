from typing import Dict, List, TYPE_CHECKING, Set, Union
import asyncio
import re
import aiofiles
from aiofiles import os as aiofiles_os
import os
import json
from datetime import datetime
from zoneinfo import ZoneInfo
import traceback
from loguru import logger
from app.utils.vueRef import RefType
from app.core.config import settings
from app.schemas.vfnode import VFlowData
from app.schemas.fanode import FARunStatus
from app.services.messageMgr import ALL_MESSAGES_MGR
from app.schemas.farequest import (
    ValidationError,
    FANodeUpdateType,
    FANodeUpdateData,
    SSEResponse,
    SSEResponseData,
    SSEResponseType,
    FAWorkflowNodeResult,
    FAWorkflowResult,
    FAWorkflow,
)
from app.db.session import get_db_ctxmgr
from app.models.fastore import (
    FAWorkflowModel,
    FAReleasedWorkflowModel,
    FANodeCacheModel,
)
from app.utils.tools import (
    getNestedLayout,
    regexMatchOriginalNodeId,
    regexMatchNodeId,
    concatNestedNodeId,
)
from app.utils.vueRef import serialize_ref
from app.schemas.VFNodeInterface import (
    VFNodeFlag,
    FromInnerPath,
    VFNodeContentData,
    RefItemValue,
)
from sqlalchemy import select, update, exc, exists, delete
from sqlalchemy.orm import selectinload

if TYPE_CHECKING:
    from app.nodes import FABaseNode


class CacheMgr:
    def __init__(self):
        pass

    async def set(self, cache_key: str, data: dict):
        """将缓存保存到数据库"""
        async with get_db_ctxmgr() as session:
            cache_entry = FANodeCacheModel(
                cid=cache_key,
                data=data,
                runStatus="Success",
            )
            session.add(cache_entry)
            await session.commit()

    async def get(self, cache_key: str):
        """从数据库加载缓存"""
        async with get_db_ctxmgr() as session:
            result = await session.execute(
                select(FANodeCacheModel).where(FANodeCacheModel.cid == cache_key)
            )
            cache_entry = result.scalar_one_or_none()
            return cache_entry.data if cache_entry else None

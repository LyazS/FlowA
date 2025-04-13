from typing import List, Dict, Optional
from typing import Annotated
from fastapi import Body, FastAPI
import asyncio
import uuid
import traceback
import json
import aiofiles
from aiofiles import os as aiofiles_os
from fastapi import APIRouter
from loguru import logger
from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi.background import BackgroundTasks
from sse_starlette.sse import EventSourceResponse
from app.core.config import settings
from app.schemas.VFlowData import VFlowData
from app.services.FARunner import FARunner
from app.services.FAValidator import FAValidator
from app.services.messageMgr import ALL_MESSAGES_MGR
from app.services.taskMgr import ALL_TASKS_MGR
from app.schemas.farequest import (
    ValidationError,
    FANodeUpdateType,
    FANodeUpdateData,
    SSEResponse,
    SSEResponseData,
    SSEResponseType,
    FAWorkflow,
    FAWorkflowLocation,
    FAWorkflowUpdateRequset,
    FAWorkflowReadRequest,
    FAWorkflowOperationResponse,
    FAWorkflowOperationType,
)
from app.models.fastore import (
    FAWorkflowModel,
    FAReleasedWorkflowModel,
    FANodeCacheModel,
)
from app.nodes import FLOWA_PROVIDER_REGISTRY, FANODE_REGISTRY, FANODE_CONFIG_REGISTRY
from app.nodes.BaseNode import FABaseNode


router = APIRouter()


@router.get("/initinfo")
async def get_initinfo():
    result = {}
    for pname, pd in FLOWA_PROVIDER_REGISTRY.items():
        result[pname] = pd.model_dump()
    return FAWorkflowOperationResponse(
        type=FAWorkflowOperationType.success,
        data=result,
    )


@router.get("/config")
async def nodeconfig(ntype: str):
    if ntype in FANODE_CONFIG_REGISTRY:
        node_cfg = FANODE_CONFIG_REGISTRY[ntype]
        return FAWorkflowOperationResponse(
            type=FAWorkflowOperationType.success,
            data=node_cfg,
        )
    else:
        return FAWorkflowOperationResponse(
            type=FAWorkflowOperationType.error,
            message=f"Node type {ntype} not found in FANODECOLLECTION",
        )


@router.get("/allconfig")
async def allnodeconfig():
    return FAWorkflowOperationResponse(
        type=FAWorkflowOperationType.success,
        data=FANODE_CONFIG_REGISTRY,
    )


@router.post("/refreshconfig")
async def refreshconfig(ntype: str):
    if ntype in FANODE_REGISTRY:
        FANODE_CONFIG_REGISTRY[ntype] =await FANODE_REGISTRY[ntype].getNodeConfig()
        return FAWorkflowOperationResponse(
            type=FAWorkflowOperationType.success,
            message=f"Node type {ntype} config refreshed",
            data=FANODE_CONFIG_REGISTRY[ntype],
        )
    else:
        return FAWorkflowOperationResponse(
            type=FAWorkflowOperationType.error,
            message=f"Node type {ntype} not found in FANODECOLLECTION",
        )
    pass

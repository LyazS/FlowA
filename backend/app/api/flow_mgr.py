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
from app.schemas.vfnode import VFlowData
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
    FAWorkflowNodeResult,
    FAWorkflowResult,
    FAWorkflow,
    FAWorkflowLocation,
    FAWorkflowUpdateRequset,
    FAWorkflowReadRequest,
    FAWorkflowCreateRequest,
    FAWorkflowOperationResponse,
    FAWorkflowOperationType,
    FAWorkflowInfo,
    FAReleaseWorkflowInfo,
    FAWorkflowNodeRequest,
    FAWorkflowCreateType,
    FAWorkflowDeleteRequest,
)
from app.services.FARunner import FARunner
from app.db.session import get_db_ctxmgr
from app.models.fastore import (
    FAWorkflowModel,
    FAReleasedWorkflowModel,
    FANodeCacheModel,
)
from sqlalchemy import select, update, exc, exists, delete
from app.utils.tools import getUuid

router = APIRouter()


@router.post("/create")
async def create_workflow(create_request: FAWorkflowCreateRequest):
    try:
        async with get_db_ctxmgr() as db:
            db_wf = None
            if create_request.type == FAWorkflowCreateType.new:
                if create_request.name is None:
                    raise ValueError("name is required for new workflow")
                db_wf = FAWorkflowModel(
                    wid=getUuid().replace("-", ""),
                    name=create_request.name,
                    lastModified=datetime.now(ZoneInfo("Asia/Shanghai")),
                )
            elif create_request.type == FAWorkflowCreateType.upload:
                if create_request.name is None:
                    raise ValueError("name is required for upload workflow")
                if create_request.vflow is None:
                    raise ValueError("vflow is required for upload workflow")
                db_wf = FAWorkflowModel(
                    wid=getUuid().replace("-", ""),
                    name=create_request.name,
                    curVFlow=create_request.vflow,
                    lastModified=datetime.now(ZoneInfo("Asia/Shanghai")),
                )
            elif create_request.type == FAWorkflowCreateType.release:
                if create_request.wid is None:
                    raise ValueError("wid is required for release workflow")
                if create_request.name is None:
                    raise ValueError("name is required for release workflow")
                if create_request.description is None:
                    raise ValueError("description is required for release workflow")
                if create_request.vflow is None:
                    raise ValueError("vflow is required for release workflow")
                db_wf = FAReleasedWorkflowModel(
                    wid=create_request.wid,
                    rwid=getUuid().replace("-", ""),
                    name=create_request.name,
                    description=create_request.description,
                    vflow=create_request.vflow,
                    releaseTime=datetime.now(ZoneInfo("Asia/Shanghai")),
                )
            if db_wf is None:
                raise ValueError("invalid create type")
            db.add(db_wf)
            await db.commit()
            await db.refresh(db_wf)
            return FAWorkflowOperationResponse(
                type=FAWorkflowOperationType.success,
                data=db_wf.wid,
            )
    except Exception as e:
        errmsg = traceback.format_exc()
        logger.error(f"create workflow error: {errmsg}")
        return FAWorkflowOperationResponse(
            type=FAWorkflowOperationType.error,
            message=errmsg,
        )


@router.get("/readall")
async def read_all_workflows():
    try:
        async with get_db_ctxmgr() as db:
            stmt = select(
                FAWorkflowModel.wid, FAWorkflowModel.name, FAWorkflowModel.lastModified
            )
            db_result = await db.execute(stmt)
            db_workflows = db_result.mappings().all()
            result: List[FAWorkflowInfo] = []
            for db_wf in db_workflows:
                result.append(
                    FAWorkflowInfo(
                        wid=db_wf["wid"],
                        name=db_wf["name"],
                        lastModified=db_wf["lastModified"],
                    )
                )
            # 按照最近修改时间排序
            result.sort(key=lambda x: x.lastModified, reverse=True)
            return FAWorkflowOperationResponse(
                type=FAWorkflowOperationType.success,
                data=result,
            )
    except Exception as e:
        errmsg = traceback.format_exc()
        logger.error(f"read all workflows error: {errmsg}")
        return FAWorkflowOperationResponse(
            type=FAWorkflowOperationType.error,
            message=errmsg,
        )


@router.post("/read")
async def read_workflow(read_request: FAWorkflowReadRequest):
    try:
        async with get_db_ctxmgr() as db:
            stmt = select(exists().where(FAWorkflowModel.wid == read_request.wid))
            db_result = await db.execute(stmt)
            db_exists = db_result.scalar()
            if db_exists:
                result = {}
                for location in read_request.locations:
                    if location == FAWorkflowLocation.wfname:
                        stmt = select(FAWorkflowModel.name).where(
                            FAWorkflowModel.wid == read_request.wid
                        )
                        db_result = await db.execute(stmt)
                        name = db_result.scalars().first()
                        result[location.value] = name
                    elif location == FAWorkflowLocation.vflow:
                        stmt = select(FAWorkflowModel.curVFlow).where(
                            FAWorkflowModel.wid == read_request.wid
                        )
                        db_result = await db.execute(stmt)
                        vflow = db_result.scalars().first()
                        result[location.value] = vflow
                    
                    elif location == FAWorkflowLocation.rwfname:
                        stmt = select(FAReleasedWorkflowModel.name).where(
                            FAReleasedWorkflowModel.rwid == read_request.rwid,
                            FAReleasedWorkflowModel.wid == read_request.wid,
                        )
                        db_result = await db.execute(stmt)
                        rwfname = db_result.scalars().first()
                        result[location.value] = rwfname
                    elif location == FAWorkflowLocation.release:
                        stmt = select(FAReleasedWorkflowModel.vflow).where(
                            FAReleasedWorkflowModel.rwid == read_request.rwid,
                            FAReleasedWorkflowModel.wid == read_request.wid,
                        )
                        db_result = await db.execute(stmt)
                        rvflow = db_result.scalars().first()
                        result[location.value] = rvflow
                    elif location == FAWorkflowLocation.allReleases:
                        stmt = (
                            select(FAReleasedWorkflowModel)
                            .where(FAReleasedWorkflowModel.wid == read_request.wid)
                            .order_by(FAReleasedWorkflowModel.releaseTime.desc())
                        )
                        db_result = await db.execute(stmt)
                        db_results = db_result.scalars().all()
                        wfresults = []
                        for db_res in db_results:
                            wfresults.append(
                                FAReleaseWorkflowInfo(
                                    rwid=db_res.rwid,
                                    releaseTime=db_res.releaseTime,
                                    name=db_res.name,
                                    description=db_res.description,
                                )
                            )
                        result[location.value] = wfresults
                return FAWorkflowOperationResponse(
                    type=FAWorkflowOperationType.success,
                    data=result,
                )
            else:
                return FAWorkflowOperationResponse(
                    type=FAWorkflowOperationType.error,
                    message="Workflow not found",
                )
    except Exception as e:
        errmsg = traceback.format_exc()
        logger.error(f"read workflow error: {errmsg}")
        return FAWorkflowOperationResponse(
            type=FAWorkflowOperationType.error, message=errmsg
        )


@router.post("/update")
async def update_workflow(update_request: FAWorkflowUpdateRequset):
    try:
        async with get_db_ctxmgr() as db:
            stmt = select(exists().where(FAWorkflowModel.wid == update_request.wid))
            db_result = await db.execute(stmt)
            db_exists = db_result.scalar()
            if db_exists:
                for item in update_request.items:
                    if item.location == FAWorkflowLocation.wfname and isinstance(
                        item.data, str
                    ):
                        await db.execute(
                            update(FAWorkflowModel)
                            .where(FAWorkflowModel.wid == update_request.wid)
                            .values(name=item.data)
                        )
                    elif item.location == FAWorkflowLocation.vflow and isinstance(
                        item.data, dict
                    ):
                        await db.execute(
                            update(FAWorkflowModel)
                            .where(FAWorkflowModel.wid == update_request.wid)
                            .values(curVFlow=item.data)
                        )
                    elif item.location == FAWorkflowLocation.rwfname and isinstance(
                        item.data, str
                    ):
                        await db.execute(
                            update(FAReleasedWorkflowModel)
                            .where(FAReleasedWorkflowModel.rwid == item.rwid)
                            .values(name=item.data)
                        )
                    elif (
                        item.location == FAWorkflowLocation.rwfdescription
                        and isinstance(item.data, str)
                    ):
                        await db.execute(
                            update(FAReleasedWorkflowModel)
                            .where(FAReleasedWorkflowModel.rwid == item.rwid)
                            .values(description=item.data)
                        )
                    else:
                        pass
                    pass
                # 更新最近时间
                await db.execute(
                    update(FAWorkflowModel)
                    .where(FAWorkflowModel.wid == update_request.wid)
                    .values(lastModified=datetime.now(ZoneInfo("Asia/Shanghai")))
                )
                await db.commit()
                return FAWorkflowOperationResponse(type=FAWorkflowOperationType.success)
            else:
                return FAWorkflowOperationResponse(
                    type=FAWorkflowOperationType.error,
                    message="Workflow not found",
                )

    except Exception as e:
        errmsg = traceback.format_exc()
        logger.error(f"update workflow error: {errmsg}")
        return FAWorkflowOperationResponse(
            type=FAWorkflowOperationType.error,
            message=errmsg,
        )


@router.post("/delete")
async def delete_workflow(delete_request: FAWorkflowDeleteRequest):
    try:
        async with get_db_ctxmgr() as db:
            # 使用 ORM 查询
            if delete_request.rwid is None:
                stmt = select(FAWorkflowModel).where(
                    FAWorkflowModel.wid == delete_request.wid
                )
            else:
                stmt = select(FAReleasedWorkflowModel).where(
                    FAReleasedWorkflowModel.wid == delete_request.wid,
                    FAReleasedWorkflowModel.rwid == delete_request.rwid,
                )
            result = await db.execute(stmt)
            workflow = result.scalar()

            if workflow:
                # 使用 ORM 的 delete 方法
                await db.delete(workflow)
                await db.commit()
                return FAWorkflowOperationResponse(type=FAWorkflowOperationType.success)
            else:
                return FAWorkflowOperationResponse(
                    type=FAWorkflowOperationType.error,
                    message="Workflow not found",
                )
    except Exception as e:
        errmsg = traceback.format_exc()
        logger.error(f"delete workflow error: {errmsg}")
        return FAWorkflowOperationResponse(
            type=FAWorkflowOperationType.error,
            message=errmsg,
        )


# @router.post("/deleteresult")
# async def delete_result(wid: str, tid: str):
#     try:
#         farunner: FARunner = await ALL_TASKS_MGR.get(tid)
#         if farunner:
#             await ALL_TASKS_MGR.remove(tid)

#         async with get_db_ctxmgr() as db:
#             await db.execute(
#                 delete(FAWorkflowResultModel).where(
#                     FAWorkflowResultModel.tid == tid,
#                     FAWorkflowResultModel.wid == wid,
#                 )
#             )
#             await db.commit()
#             return FAWorkflowOperationResponse(success=True)
#     except Exception as e:
#         errmsg = traceback.format_exc()
#         logger.error(f"delete result error: {errmsg}")
#         return FAWorkflowOperationResponse(success=False, message=errmsg)


# @router.get("/readallresults")
# async def read_all_results(wid: str):
#     try:
#         result = []
#         addedtid = set()
#         runnertid = await ALL_TASKS_MGR.getAllTaskID()
#         for tid in runnertid:
#             farunner: FARunner = await ALL_TASKS_MGR.get(tid)
#             if farunner and farunner.wid == wid:
#                 addedtid.add(tid)
#                 result.append(
#                     FAResultBaseInfo(
#                         tid=farunner.tid,
#                         status=farunner.status,
#                         starttime=farunner.starttime,
#                         endtime=farunner.endtime,
#                     )
#                 )

#         async with get_db_ctxmgr() as db:
#             stmt = select(
#                 FAWorkflowResultModel.tid,
#                 FAWorkflowResultModel.status,
#                 FAWorkflowResultModel.starttime,
#                 FAWorkflowResultModel.endtime,
#             ).where(FAWorkflowResultModel.wid == wid)
#             db_result = await db.execute(stmt)
#             db_results = db_result.mappings().all()
#             for db_res in db_results:
#                 tid = db_res["tid"]
#                 if tid in addedtid:
#                     continue
#                 result.append(
#                     FAResultBaseInfo(
#                         tid=db_res["tid"],
#                         status=db_res["status"],
#                         starttime=db_res["starttime"],
#                         endtime=db_res["endtime"],
#                     )
#                 )
#         # 将result按照开始时间最新在前排序
#         result.sort(
#             key=lambda x: x.starttime.replace(tzinfo=ZoneInfo("Asia/Shanghai")),
#             reverse=True,
#         )
#         return FAWorkflowOperationResponse(success=True, data=result)
#     except Exception as e:
#         errmsg = traceback.format_exc()
#         logger.error(f"read all results error: {errmsg}")
#         return FAWorkflowOperationResponse(success=False, message=errmsg)


# @router.post("/loadresult")
# async def load_result(wid: str, tid: str):
#     try:
#         test_farunner: FARunner = await ALL_TASKS_MGR.get(tid)
#         if test_farunner:
#             return FAWorkflowOperationResponse(
#                 success=True,
#                 data=test_farunner.oriflowdata,
#             )
#         else:
#             test_farunner = FARunner(tid)
#             loadOK = await test_farunner.loadResult(wid, tid)
#             if loadOK:
#                 await ALL_TASKS_MGR.add(test_farunner)
#                 return FAWorkflowOperationResponse(
#                     success=True,
#                     data=test_farunner.oriflowdata,
#                 )
#             else:
#                 return FAWorkflowOperationResponse(
#                     success=False, message="Result not found"
#                 )
#     except Exception as e:
#         errmsg = traceback.format_exc()
#         logger.error(f"load result error: {errmsg}")
#         return FAWorkflowOperationResponse(success=False, message=errmsg)

from typing import List
import os
import traceback
from fastapi import APIRouter
from loguru import logger
from datetime import datetime
from zoneinfo import ZoneInfo
from app.schemas.farequest import (
    FAWorkflowLocation,
    FAWorkflowUpdateRequset,
    FAWorkflowReadRequest,
    FAWorkflowCreateRequest,
    FAWorkflowOperationResponse,
    FAWorkflowOperationType,
    FAWorkflowInfo,
    FAReleaseWorkflowInfo,
    FAWorkflowCreateType,
    FAWorkflowDeleteRequest,
    FAClearCacheRequest,
)
from app.db.session import get_db_ctxmgr
from app.models.fastore import (
    FAWorkflowModel,
    FAReleasedWorkflowModel,
)
from sqlalchemy import select, update, exists
from app.utils.tools import getUuid
from app.core.config import settings

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
                    wid=getUuid(),
                    name=create_request.name,
                    lastModified=datetime.now(ZoneInfo("Asia/Shanghai")),
                )
            elif create_request.type == FAWorkflowCreateType.upload:
                if create_request.name is None:
                    raise ValueError("name is required for upload workflow")
                if create_request.vflow is None:
                    raise ValueError("vflow is required for upload workflow")
                db_wf = FAWorkflowModel(
                    wid=getUuid(),
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
                    rwid=getUuid(),
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

                # 删除工作流时，同时删除相关的图片文件
                workflow_images_dir = os.path.join(
                    settings.DATA_PATH,
                    "workflows",
                    delete_request.wid,
                )
                if os.path.exists(workflow_images_dir):
                    try:
                        import shutil

                        shutil.rmtree(workflow_images_dir)
                        logger.info(
                            f"Deleted workflow images directory: {workflow_images_dir}"
                        )
                    except Exception as e:
                        logger.error(
                            f"Failed to delete workflow images directory: {str(e)}"
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


@router.post("/clearcache")
async def clear_cache(clear_req: FAClearCacheRequest):
    try:
        from app.services.MemCacheMgr import _GLOBAL_CACHE, _GLOBAL_LOCK

        # 使用全局锁清除指定工作流的缓存
        async with _GLOBAL_LOCK:
            if clear_req.wid in _GLOBAL_CACHE:
                # 清除指定工作流的缓存
                _GLOBAL_CACHE.pop(clear_req.wid, None)
                logger.debug(f"Cleared memory cache for wid {clear_req.wid}")

        return FAWorkflowOperationResponse(type=FAWorkflowOperationType.success)
    except Exception as e:
        errmsg = traceback.format_exc()
        logger.error(f"clear cache error: {errmsg}")
        return FAWorkflowOperationResponse(
            type=FAWorkflowOperationType.error,
            message=errmsg,
        )

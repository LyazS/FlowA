from typing import List, Dict, Annotated
import asyncio
import uuid
import json
import traceback
from fastapi import APIRouter, Body
from loguru import logger
from fastapi.background import BackgroundTasks
from sse_starlette.sse import EventSourceResponse
from datetime import datetime
from zoneinfo import ZoneInfo
from app.core.config import settings
from app.schemas.fanode import FARunStatus
from app.schemas.vfnode import VFlowData, VFNodeFlag
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
    FAWorkflowOperationResponse,
    FAProgressRequestType,
    FAProgressRequest,
    FAWorkflowRunRequest,
    FAWorkflowRunReqType,
    FAWorkflowRunResponse,
    FAWorkflowNodeRequest,
    FAWorkflowOperationType,
)
from app.db.session import get_db_ctxmgr
from app.models.fastore import (
    FAWorkflowModel,
    FAReleasedWorkflowModel,
    FANodeCacheModel,
)
from sqlalchemy import select, update, exc, exists, delete

router = APIRouter()


@router.post("/run")
async def run_flow(run_req: FAWorkflowRunRequest) -> FAWorkflowOperationResponse:
    if settings.DEBUG:
        await asyncio.sleep(1)
    fav = FAValidator()
    flowdata = VFlowData.model_validate(run_req.vflow)

    # 检查工作流是否有效 =============================================
    validate_result = await fav.validate(run_req.wid, flowdata)
    if len(validate_result) > 0:
        return FAWorkflowOperationResponse(
            type=FAWorkflowOperationType.success,
            data=FAWorkflowRunResponse(
                type=FAWorkflowRunReqType.validation,
                validation_errors=validate_result,
            ),
        )

    # 检查是否还在运行 =============================================
    if await ALL_TASKS_MGR.isRunning(run_req.wid):
        return FAWorkflowOperationResponse(
            type=FAWorkflowOperationType.success,
            message="Workflow is running",
            data=FAWorkflowRunResponse(
                type=FAWorkflowRunReqType.isrunning,
            ),
        )

    # 开始运行 =============================================
    await ALL_TASKS_MGR.start_run(run_req.wid, run_req.vflow)
    logger.debug(f"running workflow: {ALL_TASKS_MGR.tasks.keys()}")

    try:
        async with get_db_ctxmgr() as db:
            await db.execute(
                update(FAWorkflowModel)
                .where(FAWorkflowModel.wid == run_req.wid)
                .values(
                    curVFlow=run_req.vflow,
                    lastModified=datetime.now(ZoneInfo("Asia/Shanghai")),
                )
            )
            await db.commit()

    except Exception as e:
        errmsg = traceback.format_exc()
        logger.error(f"update workflow error: {errmsg}")
        return FAWorkflowOperationResponse(
            type=FAWorkflowOperationType.error,
            message=errmsg,
            data=FAWorkflowRunResponse(
                type=FAWorkflowRunReqType.internalerror,
            ),
        )
    return FAWorkflowOperationResponse(
        type=FAWorkflowOperationType.success,
        data=FAWorkflowRunResponse(
            type=FAWorkflowRunReqType.success,
        ),
    )


@router.post("/stop")
async def stop_flow(stop_req: FAWorkflowRunRequest) -> FAWorkflowOperationResponse:
    if await ALL_TASKS_MGR.isRunning(stop_req.wid):
        await ALL_TASKS_MGR.stop(stop_req.wid)
        logger.debug(f"running workflow: {ALL_TASKS_MGR.tasks.keys()}")
        return FAWorkflowOperationResponse(
            type=FAWorkflowOperationType.success,
            message="Workflow stopped",
        )
    else:
        return FAWorkflowOperationResponse(
            type=FAWorkflowOperationType.error,
            message="Not found the Workflow",
        )
    pass


@router.get("/status")
async def get_flow_status(wid: str) -> FAWorkflowOperationResponse:
    if await ALL_TASKS_MGR.isRunning(wid):
        return FAWorkflowOperationResponse(
            type=FAWorkflowOperationType.success,
            data=True,
        )
    else:
        return FAWorkflowOperationResponse(
            type=FAWorkflowOperationType.success,
            data=False,
        )
    pass


@router.post("/noderequest")
async def node_request(node_req: FAWorkflowNodeRequest) -> FAWorkflowOperationResponse:
    if not await ALL_TASKS_MGR.isRunning(node_req.wid):
        return FAWorkflowOperationResponse(
            type=FAWorkflowOperationType.error,
            message="Workflow not running",
        )

    if farunner := await ALL_TASKS_MGR.get(node_req.wid):
        if node := farunner.getNode(node_req.nid):
            return FAWorkflowOperationResponse(
                type=FAWorkflowOperationType.success,
                data=node.processRequest(node_req.request),
            )
        else:
            return FAWorkflowOperationResponse(
                type=FAWorkflowOperationType.error,
                message="Node not found",
            )
    else:
        return FAWorkflowOperationResponse(
            type=FAWorkflowOperationType.error,
            message="Workflow not found",
        )
        pass
    pass


@router.post("/progress")
async def get_task_progress(prequest_body: Annotated[str, Body()]):
    prequest = FAProgressRequest.model_validate_json(prequest_body)
    wname = f"{prequest.wid}/{prequest.type.value}"

    async def event_generator():
        if await ALL_MESSAGES_MGR.has(wname):
            return
        try:
            fetch_nids = []
            # 第一步，创建消息管理器
            # 推送整体情况
            # 推送剩余情况
            # 在进度完成后，叫前端post获取一次完整结果
            await ALL_MESSAGES_MGR.create(wname)
            logger.info(f"subscribe progress {wname}")

            if not await ALL_TASKS_MGR.isRunning(prequest.wid):
                raise Exception("Not found the Workflow, subscribe failed")
            farunner: FARunner = await ALL_TASKS_MGR.get(prequest.wid)
            all_sse_data: List[SSEResponseData] = []
            if prequest.type == FAProgressRequestType.VFlowUI:
                for nid in farunner.nodes.keys():
                    node = farunner.getNode(nid)
                    if node.data.flag & VFNodeFlag.isTask:
                        fetch_nids.append(nid)
                    pass
                pass
            elif prequest.type == FAProgressRequestType.JinJa:
                fetch_nids = prequest.selected_nids
                pass
            for nid in fetch_nids:
                if nid not in farunner.nodes:
                    logger.warning(f"node {nid} not found in task {wname}")
                    continue
                if prequest.type == FAProgressRequestType.JinJa:
                    await farunner.nodes[nid].processRequest({"action": "start"})
                    pass
                ndata = await farunner.nodes[nid].getCurData()
                if ndata is None:
                    continue
                sse_data = SSEResponseData(
                    nid=nid,
                    oriid=farunner.nodes[nid].oriid,
                    data=ndata,
                )
                all_sse_data.append(sse_data)
                pass
            if prequest.type == FAProgressRequestType.VFlowUI:
                # 这里连带Passive节点的状态一起推送
                # 需要手动构建他的状态
                for nid in farunner.nodes.keys():
                    node = farunner.getNode(nid)
                    if node.data.flag & VFNodeFlag.isPassive:
                        sse_data = SSEResponseData(
                            nid=nid,
                            oriid=farunner.nodes[nid].oriid,
                            data=[
                                FANodeUpdateData(
                                    type=FANodeUpdateType.overwrite,
                                    path=["state", "status"],
                                    data=FARunStatus.Passive,
                                )
                            ],
                        )
                        all_sse_data.append(sse_data)
                        pass
                    pass
                pass
            ALL_MESSAGES_MGR.put(
                wname,
                SSEResponse(
                    event=SSEResponseType.batchupdatenode,
                    data=all_sse_data,
                ),
            )
            if farunner.status == FARunStatus.Success:
                ALL_MESSAGES_MGR.put(
                    wname,
                    SSEResponse(
                        event=SSEResponseType.flowfinish,
                        data=None,
                    ),
                )
            pass
            while True:
                # 第二步,去检查各个未完成任务的进度
                p_msg = await ALL_MESSAGES_MGR.get(wname)
                # if p_msg is None:
                #     continue
                # if prequest.node_type == FAProgressNodeType.SELECTED:
                #     logger.debug(p_msg.model_dump_json(indent=2))
                yield p_msg.toSSEResponse()
                ALL_MESSAGES_MGR.task_done(wname)
                if p_msg.event == SSEResponseType.flowfinish:
                    break
                pass

        except Exception as e:
            error_msg = traceback.format_exc()
            logger.error(error_msg)
            pass
        finally:
            await ALL_MESSAGES_MGR.remove(wname)
            if prequest.type == FAProgressRequestType.JinJa:
                for nid in fetch_nids:
                    await farunner.nodes[nid].processRequest({"action": "stop"})
                    pass
                pass
            pass
            logger.info(f"unsubscribe progress {wname}")
            pass

    return EventSourceResponse(event_generator())

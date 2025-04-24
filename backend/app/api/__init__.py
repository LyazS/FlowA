# api/__init__.py
# 初始化API，路由注册

from fastapi import APIRouter

from app.api import flow_mgr, node_mgr, run_flow, frontend

api_router = APIRouter()
api_router.include_router(run_flow.router, prefix="/api", tags=["api"])
api_router.include_router(node_mgr.router, prefix="/node", tags=["node"])
api_router.include_router(flow_mgr.router, prefix="/workflow", tags=["workflow"])
api_router.include_router(frontend.router, tags=["frontend"])

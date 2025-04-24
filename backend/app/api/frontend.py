import os
from fastapi import APIRouter, HTTPException, FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

router = APIRouter()

# 设置前端静态文件目录
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "frontend", "dist")

# 用于在应用启动时挂载静态文件
def mount_static_files(app: FastAPI):
    if os.path.exists(frontend_path):
        # 挂载静态文件
        app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="assets")

# 添加根路由处理，返回index.html
@router.get("/", include_in_schema=False)
async def serve_frontend():
    if os.path.exists(frontend_path):
        return FileResponse(os.path.join(frontend_path, "index.html"))
    else:
        raise HTTPException(status_code=404, detail="Frontend not found")

# 处理其他静态文件
@router.get("/{file_path:path}", include_in_schema=False)
async def serve_static_files(file_path: str):
    # 如果请求的是API路径，则跳过
    if file_path.startswith("api/") or file_path.startswith("node/") or file_path.startswith("workflow/"):
        raise HTTPException(status_code=404, detail="Not found")

    if not os.path.exists(frontend_path):
        raise HTTPException(status_code=404, detail="Frontend not found")

    # 检查文件是否存在
    full_path = os.path.join(frontend_path, file_path)
    if os.path.exists(full_path) and os.path.isfile(full_path):
        return FileResponse(full_path)

    # 如果文件不存在，返回index.html（用于SPA路由）
    return FileResponse(os.path.join(frontend_path, "index.html"))

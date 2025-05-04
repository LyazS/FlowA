import os
import uuid
import aiofiles
import mimetypes
from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Path
from fastapi.responses import FileResponse, JSONResponse
from app.core.config import settings

router = APIRouter()

WORKFLOW_DATA_DIR = os.path.join(settings.DATA_PATH, "workflows")
def init_file_mgr():
    # 基础数据目录
    os.makedirs(settings.DATA_PATH, exist_ok=True)
    os.makedirs(WORKFLOW_DATA_DIR, exist_ok=True)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...), wid: str = Query(..., description="工作流ID")):
    """
    上传文件并返回访问URL，按工作流ID组织
    """
    # 验证文件类型
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="只允许上传图片文件")

    # 确保工作流目录存在
    workflow_dir = os.path.join(WORKFLOW_DATA_DIR, wid)
    os.makedirs(workflow_dir, exist_ok=True)

    # 生成唯一文件名
    file_extension = os.path.splitext(file.filename)[1] if file.filename else ".png"
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(workflow_dir, unique_filename)

    # 保存文件
    try:
        async with aiofiles.open(file_path, "wb") as out_file:
            content = await file.read()
            await out_file.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")

    # 构建访问URL
    file_url = f"{wid}/{unique_filename}"

    return {"url": file_url}

@router.get("/get/{wid}/{filename}")
async def get_file(wid: str, filename: str):
    """
    获取指定工作流ID下的文件
    """
    # 构建文件路径
    file_path = os.path.join(WORKFLOW_DATA_DIR, wid, filename)

    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")

    # 获取文件的MIME类型
    content_type, _ = mimetypes.guess_type(file_path)
    if not content_type:
        content_type = "application/octet-stream"

    # 返回文件
    return FileResponse(
        path=file_path,
        media_type=content_type,
        filename=filename
    )

@router.delete("/delete/{wid}/{filename}")
async def delete_file(wid: str = Path(..., description="工作流ID"), filename: str = Path(..., description="文件名")):
    """
    删除指定工作流ID下的图片文件
    """
    # 构建文件路径
    file_path = os.path.join(WORKFLOW_DATA_DIR, wid, filename)

    # 检查文件是否存在
    if not os.path.exists(file_path):
        return JSONResponse(
            status_code=404,
            content={"message": "文件不存在", "filename": filename}
        )

    # 检查是否为图片文件
    content_type, _ = mimetypes.guess_type(file_path)
    if not content_type or not content_type.startswith("image/"):
        return JSONResponse(
            status_code=400,
            content={"message": "不是图片文件", "filename": filename}
        )

    # 删除文件
    try:
        os.remove(file_path)
        return JSONResponse(
            status_code=200,
            content={"message": "文件删除成功", "filename": filename}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件删除失败: {str(e)}")

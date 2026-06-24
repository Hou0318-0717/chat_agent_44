from fastapi import APIRouter, UploadFile, File
from ai.tool.data_tool import upload_file, process_missing, get_full_data
import json

data_router = APIRouter()


@data_router.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        result = upload_file(file)
        return {"code": 200, "data": result}
    except Exception as e:
        return {"code": 500, "msg": f"上传失败: {e}"}


@data_router.post("/process_missing")
async def process(body: dict):
    try:
        file_name = body.get("file_name")
        strategy = body.get("strategy", "drop")
        columns = body.get("columns", None)
        result = process_missing(file_name, strategy, columns)
        if "error" in result:
            return {"code": 500, "msg": result["error"]}
        return {"code": 200, "data": result}
    except Exception as e:
        return {"code": 500, "msg": f"处理失败: {e}"}


@data_router.get("/full_data")
async def full_data(file_name: str):
    try:
        result = get_full_data(file_name)
        if "error" in result:
            return {"code": 500, "msg": result["error"]}
        return {"code": 200, "data": result}
    except Exception as e:
        return {"code": 500, "msg": f"获取数据失败: {e}"}

from fastapi import APIRouter, Query
from ai.tool.chart_tool import generate_chart
import json

chart_router = APIRouter()

@chart_router.get("/chart/generate")
def generate_chart_api(
    chart_type: str = Query(..., description="bar/line/pie"),
    title: str = Query(..., description="图表标题"),
    data_json: str = Query(..., description="数据系列 JSON"),
    x_data_json: str = Query(..., description="X轴标签 JSON")
):
    """图表生成 API，返回 ECharts 配置 JSON"""
    try:
        data = json.loads(data_json)
        x_data = json.loads(x_data_json)
        result = generate_chart(chart_type, title, data, x_data)
        return {"code": 200, "data": json.loads(result)}
    except Exception as e:
        return {"code": 500, "msg": str(e)}

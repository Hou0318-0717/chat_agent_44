from pydantic import BaseModel, Field
from langchain.tools import tool
from pyecharts.charts import Bar, Line, Pie
from pyecharts import options as opts
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Noto Sans SC']
plt.rcParams['axes.unicode_minus'] = False
import json
import os
import time
import numpy as np

class ChartParams(BaseModel):
    chart_type: str = Field(..., description="图表类型: bar(柱状图), line(折线图), pie(饼图)")
    title: str = Field(..., description="图表标题")
    data_json: str = Field(..., description='数据系列 JSON: [{"name":"系列名","data":[10,20]}]')
    x_data_json: str = Field(..., description='X轴/分类标签 JSON: ["一月","二月"]')

THEME_COLORS = ["#667eea", "#764ba2", "#00d4ff", "#f093fb", "#4facfe", "#43e97b"]

def generate_chart(chart_type: str, title: str, data: list, x_data: list) -> str:
    """核心生成函数（供 agent 和 API 复用）"""
    if chart_type == "pie":
        chart = Pie()
        series_data = data[0]["data"]
        if series_data and isinstance(series_data[0], dict):
            pie_data = [[d["name"], d["value"]] for d in series_data]
        else:
            pie_data = [list(z) for z in zip(x_data, series_data)]
        chart.add("", pie_data, center=["50%", "42%"], radius=["0%", "55%"],
                  label_line_opts=opts.PieLabelLineOpts(length=8, length_2=12, smooth=False))
        chart.set_series_opts(
            label_opts=opts.LabelOpts(
                formatter="{b}({d}%)",
                font_size=11,
                position="outside"
            )
        )
    elif chart_type == "line":
        chart = Line()
        chart.add_xaxis(x_data)
        for s in data:
            chart.add_yaxis(s["name"], s["data"], is_smooth=True)
    else:
        chart = Bar()
        chart.add_xaxis(x_data)
        for s in data:
            chart.add_yaxis(s["name"], s["data"])

    chart.set_colors(THEME_COLORS)

    global_opts = {
        "title_opts": opts.TitleOpts(title=title, title_textstyle_opts=opts.TextStyleOpts(font_size=16, color="#1a1a2e")),
        "tooltip_opts": opts.TooltipOpts(
            trigger="axis" if chart_type != "pie" else "item",
            axis_pointer_type="cross" if chart_type != "pie" else None
        ),
        "legend_opts": opts.LegendOpts(textstyle_opts=opts.TextStyleOpts(color="#333"))
    }

    if chart_type != "pie":
        global_opts["toolbox_opts"] = opts.ToolboxOpts(
            feature={
                "saveAsImage": {"title": "下载"},
                "restore": {"title": "重置"}
            }
        )
    else:
        global_opts["toolbox_opts"] = opts.ToolboxOpts(
            feature={
                "saveAsImage": {"title": "下载"},
                "restore": {"title": "重置"}
            }
        )

    if chart_type != "pie":
        label_count = len(x_data)
        rotate_angle = 0
        bottom_margin = 50
        if label_count > 8:
            rotate_angle = 45
            bottom_margin = 90
        if label_count > 15:
            rotate_angle = 90
            bottom_margin = 120

        global_opts["xaxis_opts"] = opts.AxisOpts(
            axislabel_opts=opts.LabelOpts(rotate=rotate_angle, font_size=11),
            name_location="middle",
            name_gap=35
        )
        global_opts["yaxis_opts"] = opts.AxisOpts(
            axislabel_opts=opts.LabelOpts(font_size=11)
        )
        global_opts["datazoom_opts"] = [
            opts.DataZoomOpts(range_start=0, range_end=100, orient="horizontal", pos_bottom="5px"),
            opts.DataZoomOpts(type_="inside", range_start=0, range_end=100)
        ]

    if chart_type == "pie":
        global_opts["legend_opts"] = opts.LegendOpts(
            type_="scroll",
            pos_left="center",
            pos_bottom="0%",
            orient="horizontal",
            item_gap=10,
            item_width=12,
            item_height=12,
            textstyle_opts=opts.TextStyleOpts(font_size=11, color="#333")
        )

    chart.set_global_opts(**global_opts)

    if chart_type != "pie":
        chart.options["grid"] = {
            "left": "2%",
            "right": "3%",
            "bottom": f"{bottom_margin + 40}px",
            "containLabel": True
        }

    return chart.dump_options()

@tool("chart_tool", args_schema=ChartParams)
def chart_tool(chart_type: str, title: str, data_json: str, x_data_json: str) -> str:
    """生成数据可视化图表，使用Pyecharts生成ECharts配置JSON"""
    data = json.loads(data_json)
    x_data = json.loads(x_data_json)
    return generate_chart(chart_type, title, data, x_data)

def render_chart_to_image(option: dict) -> str:
    chart_type = option.get("series", [{}])[0].get("type", "bar")
    title = option.get("title", [{}])[0].get("text", "")
    x_data = [str(d) for d in option.get("xAxis", [{}])[0].get("data", [])]

    fig, ax = plt.subplots(figsize=(10, 5.5))
    fig.patch.set_facecolor('white')
    colors = ["#667eea", "#764ba2", "#00d4ff", "#f093fb", "#4facfe", "#43e97b"]

    if chart_type == "pie":
        pie_data = option.get("series", [{}])[0].get("data", [])
        labels = [d["name"] if isinstance(d, dict) else str(d) for d in pie_data]
        values = [d["value"] if isinstance(d, dict) else d for d in pie_data]
        wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%',
                                           colors=colors[:len(values)], startangle=90)
        for t in autotexts:
            t.set_color('white')
            t.set_fontsize(10)
    elif chart_type == "line":
        for si, s in enumerate(option.get("series", [])):
            y_data = s.get("data", [])
            y_points = [d[1] if isinstance(d, list) else d for d in y_data]
            x_labels = [d[0] if isinstance(d, list) else x_data[di] for di, d in enumerate(y_data)]
            ax.plot(x_labels, y_points, marker='o', color=colors[si % len(colors)],
                    label=s.get("name", ""), linewidth=2, markersize=4)
        ax.legend(loc='upper left')
        ax.tick_params(axis='x', rotation=25, labelsize=10)
    else:
        series_list = option.get("series", [])
        n_series = max(len(series_list), 1)
        width = 0.75 / n_series
        x_pos = np.arange(len(x_data))
        for si, s in enumerate(series_list):
            y_data = s.get("data", [])
            ax.bar(x_pos + si * width, y_data, width, color=colors[si % len(colors)],
                   label=s.get("name", ""))
        ax.set_xticks(x_pos + (n_series - 1) * width / 2)
        ax.set_xticklabels(x_data, rotation=25, fontsize=10)
        if n_series > 1:
            ax.legend(loc='upper left')

    ax.set_title(title, fontsize=15, fontweight='bold', color="#1a1a2e")
    ax.set_facecolor('#fafafa')
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()

    from dotenv import load_dotenv
    load_dotenv()
    file_path = os.getenv("FILE_PATH", "./static")
    file_name = f"chart_{time.strftime('%Y%m%d%H%M%S')}_{int(time.time()*1000) % 10000}.png"
    full_path = os.path.join(file_path, file_name)
    plt.savefig(full_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return full_path

if __name__ == "__main__":
    rs = chart_tool.invoke({
        "chart_type": "bar",
        "title": "月销售额",
        "data_json": '[{"name":"销售额","data":[120,200,150,80]}]',
        "x_data_json": '["一月","二月","三月","四月"]'
    })
    print("=== Bar Chart JSON ===")
    print(rs)

    rs = chart_tool.invoke({
        "chart_type": "line",
        "title": "各品类销售趋势",
        "data_json": '[{"name":"手机","data":[100,150]},{"name":"电脑","data":[200,180]}]',
        "x_data_json": '["Q1","Q2"]'
    })
    print("\n=== Line Chart JSON ===")
    print(json.dumps(json.loads(rs), indent=2, ensure_ascii=False))

    rs = chart_tool.invoke({
        "chart_type": "pie",
        "title": "品类占比",
        "data_json": '[{"name":"占比","data":[35,25,20,20]}]',
        "x_data_json": '["手机","电脑","平板","配件"]'
    })
    print("\n=== Pie Chart JSON ===")
    print(json.dumps(json.loads(rs), indent=2, ensure_ascii=False))

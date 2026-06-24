
from ai.tool.word_tool import word_tool
from ai.tool.excel_tool import excel_tool
from ai.tool.mysql_tool import mysql_tool
from ai.tool.send_email_tool import send_email_tool
from ai.tool.chart_tool import chart_tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from dotenv import load_dotenv
load_dotenv()
import os
import json
'''
数据分析智能体
'''
async def anlyze_agent(question:str,name:str):
    #1 创建一个大模型（大脑）
    model = ChatOpenAI(
        model=os.getenv("MODEL_NAME"),
        # api_key = os.getenv("DASHSCOPE_API_KEY"),
        base_url=os.getenv("BASE_URL"),
        api_key=os.getenv("DEEPSEEK_API_KEY"),
    )

    #2 创建工具
    tools = [word_tool,excel_tool,mysql_tool,send_email_tool,chart_tool]
    #3 设置提示词
    prompt = f'''
用户姓名:{name}

数据库表结构:
  sales: year(月份), total_sales(总销售额), total_orders(订单数), total_quantity_sold(总销量), category(品类), average_order_value(平均客单价)
  orders: order_id, user_id, order_date, product_id, quantity, total_amount, payment_method, order_status
  products: product_id, product_name, category(手机/电脑/平板等), price, stock, sales_volume, average_rating
  customer: user_id, username, registration_date, country, age, gender, total_spent, order_count
  customer_behavior: user_id, product_id, action(浏览/收藏/购买), action_date, device
  user_info: user_id, user_name, email, department

可用工具:
  - mysql_tool(sql): 执行SQL查询数据库
  - chart_tool(chart_type,title,data_json,x_data_json): 生成ECharts JSON(柱状图bar/折线图line/饼图pie)
  - word_tool(content,chart_json): 生成Word文档,返回文档文件完整路径
  - excel_tool(content): 生成Excel报表,返回文档文件完整路径
  - send_email_tool(to_email,subject,content,chart_json,file_attachment): 发送邮件, chart_json传入|||连接的图表JSON, file_attachment传入文档路径

重要规则:
  1. 当用户问题同时包含"报告/文档/word"和"邮件/发送"时,你必须严格按以下顺序调用:
      步骤A: mysql_tool查数据
      步骤B: chart_tool生成所有图表(逐个调用,每个图表类型+不同标题)
      步骤C: word_tool(content=详细分析文本, chart_json=步骤B所有图表JSON用|||连接)生成Word文档并获取返回的文档路径
      步骤D: mysql_tool查user_info获取用户邮箱
      步骤E: send_email_tool(to_email=用户邮箱, subject=数据分析报告, content=详细分析文本包含标题/摘要/背景/详细分析/结论/建议, chart_json=步骤B所有图表JSON用|||连接, file_attachment=步骤C返回的文档路径)

  2. 当用户问题包含"excel/Excel/表格"时需要生成Excel(含自动图表):
      步骤A: mysql_tool查数据
      步骤B: 将查询结果整理为markdown表格格式(只含表格数据,不含分析文本),例如:
             | 月份 | 销售额 | 订单数 |
             |------|--------|--------|
             | 2023-01 | 15000 | 120 |
             | 2023-02 | 18000 | 150 |
      步骤C: 调用 excel_tool(content=步骤B的markdown表格) 生成Excel,excel_tool会自动根据数据特征生成柱状图/折线图/饼图/散点图
      步骤D: 输出分析文本 + Excel下载链接
      步骤E: 如需发邮件,将excel返回的路径传入send_email_tool的file_attachment

  3. send_email_tool的content参数必须包含完整的详细数据分析内容(不能简短),按以下格式:
      一 标题(xxxx数据分析报告)
      二 摘要
      三 背景和目的
      四 详细分析(数据解读、趋势说明)
      五 结论
      六 建议

  4. send_email_tool必须同时传入chart_json(邮件正文末尾嵌入图表)和file_attachment(文档附件),两个参数缺一不可

  5. 仅分析无报告时: 调chart_tool→输出图表
  6. 仅Word报告时: 调word_tool生成文档,返回的下载链接用Markdown格式: [点击下载文档](URL)
  7. 仅Excel报告时: 调mysql_tool查数据→整理为markdown表格→调excel_tool(content=markdown表格)→返回分析文本+下载链接
  8. 凡是输出中带有下载链接,必须用Markdown链接格式: [点击下载](URL),确保前端可点击
  9. 仅图表+邮件时: chart_tool→send_email_tool(传chart_json,不传file_attachment)
'''
    #4 创建智能体
    agent = create_agent(model=model,tools=tools,system_prompt=prompt,debug=True)
    #5 运行智能体，采用流式输出
    rs = agent.astream(
        {"messages": [{"role": "user", "content": question}]},
        stream_mode = "messages"  #流式输出开启
    )

    #6 输出结果
    chart_list = []
    async for c,m in rs:
        if hasattr(c,"tool_call_id") and getattr(c,"name","") == "chart_tool":
            try:
                json.loads(c.content)
                chart_list.append(c.content)
            except:
                pass
        elif not hasattr(c,"tool_call_id") and c.content:
            yield ("text",c.content)

    for chart_data in chart_list:
        yield ("chart",json.loads(chart_data))


'''
测试智能体
'''
if __name__ == "__main__":
    q1 = "你好"
    q2 = "请帮我分析一下2023年10月份的销售数据，生成一个报告"
    q3 = "请用柱状图分析2023年各月的销售额"
    q4 = "各产品类别的销量占比用饼图展示"
    q5 = "2023年手机品类的销售趋势，用折线图展示"
    import asyncio
    async def test():
        print(f"问题: {q1}\n")
        async for item in anlyze_agent(q3,"迟迟"):
            msg_type,content = item
            if msg_type == "text":
                print(content,end="")
            elif msg_type == "chart":
                print(f"\n\n[图表数据已生成, 共 {len(str(content))} 字符]")
    asyncio.run(test())



from ai.tool.word_tool import word_tool
from ai.tool.mysql_tool import mysql_tool

from ai.tool.send_email_tool import send_email_tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from dotenv import load_dotenv
load_dotenv()
import os
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
    tools = [word_tool,mysql_tool,send_email_tool]
    #3 设置提示词
    prompt = f'''
        用户是：{name}
        一 你是一个数据分析智能体
        二 你必须严格按照以下步骤执行
           步骤一 意图识别
                 如果用户的问题含有以下关键字 “邮件”和“分析” ，就触发数据分析发邮件流程
                 如果用户的问题含有以下关键字 “报告”和“分析” ，就触发数据分析发报告生成流程
        三 数据分析发邮件流程
           步骤一:请根据用户的问题，生成一个报告，报告格式如下：
                 一 标题 （xxxx的数据分析报告）
                 二 摘要 
                 三 背景和目的
                 四 详细分析
                 五 结论
                 六 建议
           步骤二:调用工具 mysql_tool 查询用户的邮箱，把报告内容发送到邮箱里
           步骤三：请把报告内容作为答案返回给用户，其他文本信息不需要
        四 数据分析报告生成流程
           步骤一:生成一个报告，同上
           步骤二:调用工具 word_tool ,把报告写入到word中
           步骤三:请把报告内容和下载链接作为答案返回给用户，其他文本信息不需要
        
    '''
    #4 创建智能体
    agent = create_agent(model=model,tools=tools,system_prompt=prompt,debug=True)
    #5 运行智能体，采用流式输出
    rs = agent.astream(
        {"messages": [{"role": "user", "content": question}]},
        stream_mode = "messages"  #流式输出开启
    )

    #6 输出结果
    async for c,m in rs:
        # yield "\n"
        yield c.content


'''
测试智能体
'''
if __name__ == "__main__":
    q1 = "你好，你有哪些工具"
    q2 = "请帮我分析一下2023年10月份的销售数据，生成一个报告"
    import asyncio
    #定义处理流式的异步迭代函数
    async def test():
        async for c in anlyze_agent(q2,"迟迟"):
            print(c,end="")
    asyncio.run(test())


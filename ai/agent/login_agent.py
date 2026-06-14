from ai.tool.send_email_tool import send_email_tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from dotenv import load_dotenv
import os

#读取配置文件.env
load_dotenv()
'''
登录智能体
1 通过自然语言方式，让AI去发邮件
'''
def login_agent(question:str):
    #1 创建一个大模型(大脑)
    model = ChatOpenAI(
        model = os.getenv("MODEL_NAME"),
        # api_key = os.getenv("DASHSCOPE_API_KEY"),
        base_url = os.getenv("BASE_URL"),
        api_key=os.getenv("DEEPSEEK_API_KEY"),
    )
    #2 创建工具
    tools = [send_email_tool]
    #3 定义提示词
    prompt = '''
       ——你是一个邮件发送助手
    '''
    #创建智能体
    agent = create_agent(model=model, tools=tools,system_prompt=prompt,debug=True)
    #5 运行智能体
    rs = agent.invoke(
        {"messages":[{"role":"user","content":question}]}
    )
    print(rs)
    print(rs["messages"][-1].content)


'''
测试智能体
'''
if __name__ == "__main__":
    q1="给用户2118541898@qq.com发送一份邮件，告诉他今天下午三点来上课！"
    login_agent(q1)
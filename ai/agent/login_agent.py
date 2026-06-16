from ai.tool.mysql_tool import mysql_tool
from ai.tool.redis_tool import redis_get_tool
from ai.tool.redis_tool import redis_set_tool
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
    tools = [send_email_tool,mysql_tool,redis_set_tool]
    #3 定义提示词
    prompt = '''
       一 你是一个邮件发送助手
        二 业务流程
          1: 意图识别
             如果用户问题含有以下关键字, ‘邮件’，就触发发送验证码流程
             如果用户问题含有以下关键字, ‘验证码’，就触发登录流程
          2: 发送验证码流程
             步骤一:调用工具 mysql_tool 验证邮箱是否存在
             步骤二:随机生成一个4位数的数字作为验证码
             步骤三:发送一封邮件,邮件标题：三峡科技大学验证码  邮件内容：你的验证码是:xxxx
             步骤四:如果邮箱不存在，请告知用户：邮箱未注册，请注册，其它文本信息不需要
             步骤五：如果邮件发送成功，请告知用户：验证码已经发送，其它文本信息不需要
          3：登录流程
             步骤一：验证用户输入的验证码和redis缓存的验证码进行校验
             步骤二：如果校验正确，请查询用户名，返回给用户
             步骤三：请返回给用户的答案是：登录成功:用户名 ,其它文本信息不需要
    '''
    #4 创建智能体
    agent = create_agent(model=model, tools=tools,system_prompt=prompt,debug=True)
    #5 运行智能体
    rs = agent.invoke(
        {"messages":[{"role":"user","content":question}]}
    )
    #print(rs)
    print(rs["messages"][-1].content)
    return rs["messages"][-1].content


'''
测试智能体
'''
if __name__ == "__main__":
    q1="给用户2118541898@qq.com发送一份邮件，告诉他今天下午三点来上课！"
    q2="你是谁，你有哪些工具"
    q3="邮件：2118541898@qq.com"
    q4="邮件：2118541898@qq.com,验证码8732"
    login_agent(q4)
from email.mime.multipart import MIMEMultipart

import dotenv
from pydantic import BaseModel,Field
from langchain.tools import tool
from email.mime.text import MIMEText
import smtplib
from dotenv import load_dotenv
import os

#读取配置文件.env
load_dotenv()
'''
第一步，先定义工具需要的参数，通常参数是用类的方式进行封装
'''
class EmailParams(BaseModel):
    to_email:str = Field(...,description="收件人邮箱")
    subject:str = Field(...,description="邮件标题")
    content:str = Field(...,description="邮件正文")

'''
第二步：定义工具
'''
@tool("sent_email_tool",args_schema=EmailParams)
def send_email_tool(to_email:str,subject:str,content:str) -> str:
    """
    用于邮件发送
    """
    try:
        #创建邮件对象
        msg = MIMEText(content)
        #定义收件人
        msg["To"] = to_email
        #定义发件人
        msg["From"] = os.getenv("EMAIL_USER")
        #定义邮件标题
        msg["Subject"] = subject
        #创建一个链接腾讯QQ邮件服务器
        with smtplib.SMTP_SSL(os.getenv("EMAIL_HOST")) as smtp:
            #登录邮件服务器
            smtp.login(os.getenv("EMAIL_USER"),os.getenv("EMAIL_PASSWORD"))
            #发送邮件
            smtp.sendmail(os.getenv("EMAIL_USER"),to_email,msg.as_string())
        return "邮件发送成功"

    except Exception as e:
        print(f"send_email_tool工具出现异常：{e}")
        return f"邮件发送失败:{e}"

    '''
    验证工具是否正确
    '''
if __name__ == "__main__":
    send_email_tool.invoke({"to_email":"2118541898@qq.com","subject":"测试邮件","content":"这是一封测试邮件"})
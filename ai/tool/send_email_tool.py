from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication

import dotenv
from pydantic import BaseModel,Field
from langchain.tools import tool
from email.mime.text import MIMEText
import smtplib
from dotenv import load_dotenv
from ai.tool.chart_tool import render_chart_to_image
import os
import json

#读取配置文件.env
load_dotenv()
'''
第一步，先定义工具需要的参数，通常参数是用类的方式进行封装
'''
class EmailParams(BaseModel):
    to_email:str = Field(...,description="收件人邮箱")
    subject:str = Field(...,description="邮件标题")
    content:str = Field(...,description="邮件正文")
    chart_json:str = Field(None,description="ECharts配置JSON数组字符串, 多个用 ||| 分隔")
    file_attachment:str = Field(None,description="附件文件路径(如word文档)")

'''
第二步：定义工具
'''
@tool("sent_email_tool",args_schema=EmailParams)
def send_email_tool(to_email:str,subject:str,content:str,chart_json:str = None,file_attachment:str = None)->str:
    """
    用于邮件发送，支持嵌入图表图片和文件附件
    """
    try:
        #创建外层邮件对象
        msg = MIMEMultipart("mixed")
        msg["To"] = to_email
        msg["From"] = os.getenv("EMAIL_USER")
        msg["Subject"] = subject

        html_body = f"<div style='font-size:14px;color:#333;'>{content.replace(chr(10),'<br>')}</div>"

        if chart_json:
            body_part = MIMEMultipart("related")
            chart_strs = [c.strip() for c in chart_json.split("|||") if c.strip()]
            for i, chart_str in enumerate(chart_strs):
                try:
                    option = json.loads(chart_str)
                    img_path = render_chart_to_image(option)
                    with open(img_path, 'rb') as f:
                        img = MIMEImage(f.read())
                        img.add_header('Content-ID', f'<chart_{i}>')
                        img.add_header('Content-Disposition', 'inline')
                        body_part.attach(img)
                    html_body += f'<br><img src="cid:chart_{i}" style="max-width:600px;width:100%;">'
                except Exception as e:
                    print(f"邮件插入图表{i+1}失败:", e)
            body_part.attach(MIMEText(html_body, 'html', 'utf-8'))
            msg.attach(body_part)
        else:
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))

        #添加文件附件
        if file_attachment and os.path.exists(file_attachment):
            with open(file_attachment, 'rb') as f:
                att = MIMEApplication(f.read(), _subtype="docx")
                att.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file_attachment))
                msg.attach(att)

        #创建一个链接腾讯QQ邮件服务器
        with smtplib.SMTP_SSL(os.getenv("EMAIL_HOST")) as smtp:
            smtp.login(os.getenv("EMAIL_USER"),os.getenv("EMAIL_PASSWORD"))
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
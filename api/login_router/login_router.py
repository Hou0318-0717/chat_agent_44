import email

from fastapi import APIRouter
from ai.agent.login_agent import login_agent

#创建一个登陆模型的子路由
login_router = APIRouter()
#定义发送验证码接口
@login_router.get("/send_code")
def send_code(email:str):
    #定义问题
    try:
        question = f"邮件:{email}"
        rs = login_agent(question)
        return {"code":200,"msg":rs}
    except Exception as e:
        return {"code":500,"msg":"出现异常"}

#定义一个登录接口
@login_router.get("/login")
def login(email:str,code:str):
    #定义问题
    try:
        
        question = f"邮件:{email},验证码:{code}"
        rs = login_agent(question)
        return {"code":200,"msg":rs}
    except Exception as e:
        return({"code":500,"msg":"出现异常"})
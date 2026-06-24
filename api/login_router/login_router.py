import email

from fastapi import APIRouter
from ai.agent.login_agent import login_agent
import random
import redis
import pymysql
from dotenv import load_dotenv
import os
load_dotenv()

db_url = os.getenv("DATABASE_URL")
db_root = os.getenv("DATABASE_USER")
db_password = os.getenv("DATABASE_PASSWORD")
db_port = os.getenv("DATABASE_PORT")
db_name = os.getenv("DATABASE_NAME")
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

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

#定义发送注册验证码接口
@login_router.get("/send_code_register")
def send_code_register(email: str):
    try:
        code = str(random.randint(1000, 9999))
        redis_client.set(f"register:{email}", code, ex=120)
        from ai.tool.send_email_tool import send_email_tool
        rs = send_email_tool.invoke({
            "to_email": email,
            "subject": "三峡科技大学注册验证码",
            "content": f"你的注册验证码是: {code}，120秒内有效。"
        })
        print(f"[注册验证码] {email} -> {rs}")
        if "成功" in rs:
            return {"code": 200, "msg": "验证码已发送"}
        else:
            return {"code": 500, "msg": rs}
    except Exception as e:
        print(f"[注册验证码] 异常: {e}")
        return {"code": 500, "msg": f"发送失败: {e}"}

#定义注册接口
@login_router.get("/register")
def register(email: str, code: str, userName: str, department: str = "未分配"):
    try:
        cached_code = redis_client.get(f"register:{email}")
        if cached_code is None:
            return {"code": 500, "msg": "验证码已过期，请重新发送"}
        cached_code = cached_code.decode()
        if cached_code != code:
            return {"code": 500, "msg": "验证码错误"}
        con = pymysql.connect(host=db_url, user=db_root, password=db_password,
                              port=int(db_port), db=db_name, charset="utf8")
        cursor = con.cursor()
        cursor.execute(f"SELECT * FROM user_info WHERE email='{email}'")
        if cursor.fetchone():
            cursor.close()
            con.close()
            return {"code": 500, "msg": "该邮箱已注册，请直接登录"}
        sql = f"INSERT INTO user_info(user_name, email, department) VALUES('{userName}', '{email}', '{department}')"
        cursor.execute(sql)
        con.commit()
        cursor.close()
        con.close()
        redis_client.delete(f"register:{email}")
        return {"code": 200, "msg": "注册成功"}
    except Exception as e:
        return {"code": 500, "msg": f"注册失败: {e}"}
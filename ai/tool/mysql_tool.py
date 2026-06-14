import pymysql
from pydantic import BaseModel,Field
from langchain.tools import tool
import smtplib
from dotenv import load_dotenv
import os
#加载配置文件
db_url = os.getenv("DATABASE_URL")
db_root = os.getenv("DATABASE_USER")
db_password = os.getenv("DATABASE_PASSWORD")
db_port = os.getenv("DATABASE_PORT")
db_name = os.getenv("DATABASE_NAME")
print(f"数据库地址:{db_url},用户名:{db_root},密码:{db_password},端口:{db_port},数据库名:{db_name}")
'''
sql工具函数
'''
@tool("mysql_tool")
def mysql_tool(sql:str)->tuple:
    '''
    sql执行工具
    数据库模式：
        user_info用户表  字段:user_id user_name 用户名  email 用户邮箱 department 部门
    :param sql: sql语句
    :return: 返回查询结果
    '''
    #获取数据库链接
    con = pymysql.connect(host=db_url,user=db_root,password=db_password,port=int(db_port),db=db_name,charset='utf8')
    #获取游标对象，执行sql对象
    cursor = con.cursor()
    try:
        #执行sql
        cursor.execute(sql)
        #获取结果
        rs = cursor.fetchall()
        return rs
    except Exception as e:
        print("数据库查询出现异常",e)
        return ("数据可查询出现异常",)
    finally:
        #关闭游标对象
        cursor.close()
        #关闭数据库链接
        con.close()

#测试工具是否可以使用
if __name__ == '__main__':
    rs = mysql_tool.invoke(sql="SELECT * FROM sales")
    print(rs)

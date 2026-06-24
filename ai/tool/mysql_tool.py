import pymysql
from pydantic import BaseModel,Field
from langchain.tools import tool
import smtplib
from dotenv import load_dotenv
import os

load_dotenv()
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
    """
    sql 执行工具
    数据库模式：
                        user_info 用户表 字段: user_id 用户id user_name 用户名 email 邮箱 department 部门
                       customer 客户表
                        字段：
                            user_id(用户ID) - BIGINT, 主键
                            username(用户名) - TEXT
                            registration_date(注册日期) - TEXT/DATE
                            country(国家) - TEXT
                            age(年龄) - BIGINT
                            gender(性别) - TEXT
                            total_spent(总消费金额) - DOUBLE
                            order_count(订单数量) - BIGINT
                    products 商品表
                        字段：
                            product_id(产品ID) - BIGINT, 主键
                            product_name(产品名称) - TEXT
                            category(产品类别) - TEXT
                            price(价格) - DOUBLE
                            stock(库存) - BIGINT
                            sales_volume(销售量) - BIGINT
                            average_rating(平均评分) - DOUBLE
                    orders 订单表
                        字段：
                            order_id(订单ID) - BIGINT, 主键
                            user_id(用户ID) - BIGINT, 外键(users.user_id)
                            order_date(订单日期) - TEXT/DATE
                            product_id(产品ID) - BIGINT, 外键(products.product_id)
                            quantity(数量) - BIGINT
                            total_amount(总金额) - DOUBLE
                            payment_method(支付方式) - TEXT
                            order_status(订单状态) - TEXT
                    customer_behavior 客户行为表
                        字段：
                            id(行为记录ID) - BIGINT, 主键
                            user_id(用户ID) - BIGINT, 外键(users.user_id)
                            product_id(产品ID) - BIGINT, 外键(products.product_id)
                            action(行为类型) - TEXT (浏览/收藏/购买)
                            action_date(行为日期) - TEXT/DATE
                            device(设备类型) - TEXT
                    sales 销售表
                        字段：
                            id(统计记录ID) - BIGINT, 主键
                            year(年份月份) - TEXT (格式: YYYY-MM)
                            total_sales(总销售额) - DOUBLE
                            total_orders(总订单数) - BIGINT
                            total_quantity_sold(总销售量) - BIGINT
                            category(产品类别) - TEXT
                            average_order_value(平均订单价值) - DOUBLE
    :param sql: sql语句
    :return: 返回查询结果
    """
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
        return ("数据查询出现异常",)
    finally:
        #关闭游标对象
        cursor.close()
        #关闭数据库链接
        con.close()

#测试工具是否可以使用
if __name__ == '__main__':
    rs = mysql_tool.invoke({"sql":"SELECT * FROM user_info"})
    print(rs)

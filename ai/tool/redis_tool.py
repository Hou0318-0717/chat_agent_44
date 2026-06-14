from pydantic import BaseModel,Field
from langchain.tools import tool
import redis

#创建一个redis链接
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)



'''
redis 数据设置
'''
@tool("redis_set_tool")
def redis_set_tool(key:str,value:str)->str:
    """
    把验证码存入到redis中。
    :param key:键名
    :param value:键值
    :return:返回提示信息
    """
    try:
        redis_client.set(key,value,ex=60)
        print("redis_set_tool工具执行成功")
        return "redis_set_tool工具执行成功"
    except Exception as e:
        print(f"redis_set_tool工具出现异常:{e}")
        return f"redis_set_tool工具出现异常:{e}"

'''
redis数据获取
'''
@tool("redis_get_tool")
def redis_get_tool(key:str)->str:
    """
    获取redis中的数据
    :param key:键名
    :return:返回提示信息
    """
    try:
        rs=redis_client.get(key)
        print(f"rs={rs}")
        print("redis_get_tool工具执行成功")
        if rs:
            return rs.decode()
        else:
            return "验证码过期"
    except Exception as e:
        print(f"redis_set_tool工具出现异常:{e}")
        return f"redis_set_tool工具出现异常:{e}"

'''
验证工具是否可以使用
'''
if __name__ == "__main__":
    redis_set_tool.invoke({"key":"a","value":"abcd"})
    rs = redis_get_tool.invoke({"key":"a"})
    print(rs)
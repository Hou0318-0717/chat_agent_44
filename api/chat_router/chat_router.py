from fastapi import FastAPI, APIRouter
from ai.agent.anlyze_agent import  anlyze_agent
import json
from fastapi.responses import StreamingResponse
#创建一个API路由
chat_router = APIRouter()

#创建一个接口
@chat_router.get("/chat")
def chat(question,name):

    #创建一个异步的迭代函数
    async def test():
            try:
                async for c in anlyze_agent(question,name):
                    #创建一个字典来定义数据格式
                    msg = {"done":False,"data":c}
                    #SSE流式输出格式
                    yield f"data:{json.dumps(msg)}\n\n"

                msg = {"done":True,"data":"流式结束"}
                yield f"data:{json.dumps(msg)}\n\n"


            except Exception as e:
                print("出现异常",e)
                msg = {"done":True,"data":"出现异常"}
                yield f"data:{json.dumps(msg)}\n\n"
    return StreamingResponse(test(),media_type="text/event-stream")
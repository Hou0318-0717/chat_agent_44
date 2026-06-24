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
                async for item in anlyze_agent(question,name):
                    msg_type,content = item
                    if msg_type == "text":
                        msg = {"done":False,"type":"text","data":content}
                        yield f"data:{json.dumps(msg)}\n\n"
                    elif msg_type == "chart":
                        print(f"[CHART] 图表数据已生成, 大小: {len(str(content))} 字符")
                        msg = {"done":False,"type":"chart","data":content}
                        yield f"data:{json.dumps(msg)}\n\n"

                yield f"data:{json.dumps({'done':True,'data':'流式结束'})}\n\n"


            except Exception as e:
                import traceback
                traceback.print_exc()
                msg = {"done":True,"data":"出现异常"}
                yield f"data:{json.dumps(msg)}\n\n"
    return StreamingResponse(test(),media_type="text/event-stream")
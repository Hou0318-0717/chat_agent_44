from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from api.login_router.login_router import login_router
from api.chat_router.chat_router import chat_router
from api.chart_router.chart_router import chart_router
from api.data_router.data_router import data_router
#创建一个应用程序
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],  # 前端应用地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#配置静态资源目录
app.mount("/static", StaticFiles(directory="../static"), name="static")
#注册路由
app.include_router(login_router)

app.include_router(chat_router)

app.include_router(chart_router)

app.include_router(data_router)

#创建一个登录接口
@app.get("/")
def login():
    return {"message": "Hello World"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="localhost", port=8080)

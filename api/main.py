from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.login_router.login_router import login_router

#创建一个应用程序
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # 前端应用地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#注册路由
app.include_router(login_router)

#创建一个登录接口
@app.get("/")
def login():
    return {"message": "Hello World"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="localhost", port=8080)

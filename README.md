# AI智能数据分析助手

基于大语言模型（DeepSeek）的智能数据分析平台，通过自然语言对话实现数据查询、图表生成、报告输出等功能。

## 技术栈

| 层级 | 技术 |
|---|---|
| 前端 | Vue 2 + Element-UI + ECharts 6.0 |
| 后端 | FastAPI + Uvicorn |
| AI框架 | LangChain + LangGraph |
| 大模型 | DeepSeek（deepseek-reasoner） |
| 数据库 | MySQL 9.1 + Redis 3.0 |
| 图表 | Pyecharts 2.0 + Matplotlib 3.11 |
| 文档 | python-docx |
| 通信 | SSE (Server-Sent Events) |

## 功能特性

### ✅ 登录系统
- 邮箱验证码登录（SMTP发送 + Redis缓存，有效期120秒）
- 基于LangChain Agent的意图识别与验证码处理

### ✅ AI数据分析对话
- 自然语言查询数据库（支持多轮对话上下文）
- SSE流式输出（打字机效果实时回复）
- 支持销售、订单、产品、客户等多维度数据查询

### ✅ 图表生成
- 三种图表类型：柱状图、折线图、饼图
- Pyecharts生成ECharts JSON → 前端ECharts交互式渲染
- DataZoom缩放（底部滑块 + 鼠标滚轮）
- Toolbox工具箱（下载/缩放/重置）
- 多图表并发展示（单次查询可同时生成多个图表）
- 自定义主题配色（与前端页面风格统一）

### ✅ 报告生成与发送
- Word文档自动生成（python-docx），支持嵌入图表PNG
- 邮件发送（SMTP_SSL），支持HTML正文含图表 + Word文档附件
- 报告六段式结构：标题/摘要/背景/分析/结论/建议

### ✅ 用户注册
- 独立注册流程（区别于登录的验证码校验）
- Redis缓存注册验证码 + MySQL持久化用户信息

### ✅ 文件处理
- CSV/Excel文件上传与解析
- 6种缺失值填充策略：删除行 / 均值 / 中位数 / 众数 / 前向填充 / 插值
- 处理前后数据对比与结果下载

## 项目结构

```
sanxia_4144/
├── api/                          # FastAPI 路由层
│   ├── main.py                   # 应用入口，注册4个子路由
│   ├── login_router/             # 登录/注册接口
│   ├── chat_router/              # SSE流式对话接口
│   ├── chart_router/             # 图表生成API接口
│   └── data_router/              # 文件上传/缺失值处理接口
├── ai/
│   ├── agent/
│   │   ├── login_agent.py        # 登录智能体（3个Tool）
│   │   └── anlyze_agent.py       # 数据分析智能体（5个Tool）
│   └── tool/
│       ├── mysql_tool.py         # 数据库查询工具
│       ├── redis_tool.py         # Redis缓存工具
│       ├── send_email_tool.py    # 邮件发送工具
│       ├── chart_tool.py         # Pyecharts + Matplotlib图表
│       ├── word_tool.py          # python-docx Word文档
│       ├── excel_tool.py         # openpyxl Excel报表
│       └── data_tool.py          # pandas数据处理
├── static/                       # 静态资源（生成的文件/图片）
└── chat_agent/                   # 前端项目（Vue 2）
    └── src/components/page/
        ├── Login.vue             # 登录/注册页
        ├── Chat01.vue            # 主对话页（SSE+ECharts）
        └── DataProcess.vue       # 数据处理页
```

## 安装与运行

### 前置条件

- Python 3.12（建议Miniconda环境）
- Node.js v14.16
- MySQL 9.1
- Redis 3.0
- QQ邮箱（用于发送验证码和邮件）

### 后端安装

```bash
# 1. 创建虚拟环境
conda create -n myenv python=3.12 -y
conda activate myenv

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
# 复制 .env.example 为 .env，填写以下配置：
#   - 邮箱SMTP配置（EMAIL_USER、EMAIL_PASSWORD授权码）
#   - 数据库连接配置（DATABASE_URL/USER/PASSWORD等）
#   - DeepSeek API Key（DEEPSEEK_API_KEY）

# 4. 初始化数据库
#   使用Navicat创建 chat_agent_44 数据库，字符集utf8mb4
#   数据库包含6张表：sales、orders、products、customer、customer_behavior、user_info

# 5. 启动后端
cd api
python main.py
# 服务运行在 http://localhost:8080
```

### 前端安装

```bash
cd chat_agent
npm install
npm run dev
# 前端运行在 http://localhost:8000
```

### 环境变量说明

| 变量名 | 说明 | 示例 |
|---|---|---|
| EMAIL_USER | QQ邮箱地址 | 2118541898@qq.com |
| EMAIL_PASSWORD | QQ邮箱SMTP授权码 | 16位授权码 |
| EMAIL_HOST | SMTP服务器 | smtp.qq.com |
| DATABASE_URL | 数据库地址 | localhost |
| DATABASE_USER | 数据库用户名 | root |
| DATABASE_PASSWORD | 数据库密码 | 123456 |
| DATABASE_PORT | 数据库端口 | 3306 |
| DATABASE_NAME | 数据库名称 | chat_agent_44 |
| DEEPSEEK_API_KEY | DeepSeek API Key | sk-xxx |
| BASE_URL | DeepSeek API地址 | https://api.deepseek.com |
| MODEL_NAME | 模型名称 | deepseek-reasoner |
| FILE_PATH | 文件存储路径 | D:\project\sanxia_4144\static |

## 使用指南

1. **启动服务**：后端 `python api/main.py`，前端 `npm run dev`
2. **登录**：浏览器访问 `http://localhost:8000`，输入邮箱获取验证码
3. **数据分析**：在主对话页面输入例如：
   - `"请用柱状图分析2023年各月销售额"`
   - `"各产品类别的销量占比用饼图展示"`
   - `"帮我分析2023年10月销售数据生成报告"`
4. **数据处理**：点击侧边栏"数据处理"按钮，上传CSV/Excel文件进行缺失值处理

## 数据库表结构

| 表名 | 说明 | 主要字段 |
|---|---|---|
| sales | 销售汇总表 | year, total_sales, total_orders, category |
| orders | 订单表 | order_id, user_id, order_date, total_amount |
| products | 产品表 | product_id, product_name, category, price |
| customer | 客户表 | user_id, username, registration_date, country |
| customer_behavior | 客户行为表 | user_id, product_id, action, action_date |
| user_info | 用户表 | user_id, user_name, email, department |


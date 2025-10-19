# 外发开发指南

本文档为外部开发者提供项目开发指南，包括环境搭建、开发流程和安全规范。

## 目录
- [项目概述](#项目概述)
- [开发环境搭建](#开发环境搭建)
- [项目结构](#项目结构)
- [开发流程](#开发流程)
- [安全规范](#安全规范)
- [提交规范](#提交规范)
- [测试指南](#测试指南)
- [部署说明](#部署说明)

## 项目概述

AllSmart 智能管理系统是一个基于 FastAPI 的后台管理系统，提供用户管理、设备管理、任务管理和 API 配置等功能。

主要技术栈：
- 后端：Python 3.8+, FastAPI, SQLAlchemy
- 前端：HTML, CSS, JavaScript
- 数据库：SQLite (开发环境)
- 认证：JWT

## 开发环境搭建

### 1. 克隆项目
```bash
git clone <项目地址>
cd allsmart8
```

### 2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 配置环境变量
```bash
cp .env.example .env
```
编辑 `.env` 文件，设置合适的配置项（使用占位符值）。

### 5. 初始化数据库
```bash
python migrate_database.py
```

### 6. 启动开发服务器
```bash
python main.py
```
或
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 项目结构

```
allsmart8/
├── public/                 # 前端静态文件
│   ├── admin.html          # 管理员界面
│   ├── user.html           # 用户界面
│   └── ...                 # 其他静态资源
├── .env.example           # 环境变量示例文件
├── .gitignore             # Git忽略文件
├── README.md              # 项目说明文档
├── EXTERNAL_DEVELOPMENT.md # 外发开发指南
├── SECURITY_GUIDELINES.md  # 安全开发规范
├── auth.py                # 认证模块
├── config_sync.py         # 配置同步模块
├── crude.py               # 数据库操作模块
├── database.py            # 数据库配置模块
├── main.py                # 主应用入口
├── migrate_database.py    # 数据库迁移脚本
├── models.py              # 数据库模型
├── requirements.txt       # 项目依赖
├── schemas.py             # Pydantic模型
├── secure_keys.py         # 安全密钥管理
├── SimpleCache.py         # 简单缓存实现
└── utils.js               # 前端工具函数
```

## 开发流程

### 1. 创建功能分支
```bash
git checkout -b feature/your-feature-name
```

### 2. 开发功能
- 遵循项目代码风格
- 添加必要的注释
- 编写测试用例（如适用）

### 3. 本地测试
- 确保所有功能正常工作
- 检查是否有错误日志
- 验证安全规范是否遵守

### 4. 提交代码
```bash
git add .
git commit -m "描述你的更改"
git push origin feature/your-feature-name
```

### 5. 创建 Pull Request
在代码托管平台上创建 Pull Request，等待代码审查。

## 安全规范

详细的安全规范请参考 [SECURITY_GUIDELINES.md](SECURITY_GUIDELINES.md)。

关键要点：
1. 不要在代码中硬编码敏感信息
2. 所有敏感信息通过环境变量传递
3. 遵循最小权限原则
4. 对用户输入进行验证和过滤

## 提交规范

### 提交信息格式
```
<type>(<scope>): <subject>

<body>

<footer>
```

### 类型说明
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- style: 代码格式调整
- refactor: 代码重构
- test: 测试相关
- chore: 构建过程或辅助工具的变动

### 示例
```
feat(auth): 添加JWT令牌刷新功能

实现JWT令牌刷新接口，提高用户体验

Fixes #123
```

## 测试指南

### 单元测试
项目使用 pytest 进行单元测试（如已配置）：
```bash
pytest tests/
```

### 手动测试
1. 启动开发服务器
2. 访问 http://localhost:8000 检查前端界面
3. 访问 http://localhost:8000/docs 查看API文档并测试接口

### 安全测试
1. 验证认证和授权功能
2. 检查输入验证
3. 确保敏感信息未泄露

## 部署说明

### 开发环境部署
```bash
python main.py
```

### 生产环境部署
建议使用以下方式部署：
1. 使用 Gunicorn 或 Uvicorn 作为应用服务器
2. 使用 Nginx 作为反向代理
3. 配置 HTTPS
4. 设置合适的环境变量

### Docker 部署（如需要）
可以创建 Dockerfile 进行容器化部署：
```dockerfile
FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 联系方式

如有任何问题，请联系项目维护者：
- 邮箱: [维护者邮箱]
- Slack: [Slack频道链接]

感谢您为项目做出的贡献！
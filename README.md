# AllSmart 智能管理系统

一个基于FastAPI的用户和管理员后台管理系统，支持设备管理、任务管理、API配置等功能。

## 项目特点

- 用户认证与权限管理（用户、管理员、超级管理员）
- 设备管理
- 任务管理
- API配置管理
- 生物识别数据管理
- 前端管理界面
- 数据库加密存储敏感信息

## 环境要求

- Python 3.8+
- SQLite (默认) 或其他数据库
- Node.js (用于前端构建，可选)

## 安装步骤

1. 克隆项目代码：
   ```
   git clone <项目地址>
   cd allsmart8
   ```

2. 创建虚拟环境：
   ```
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate  # Windows
   ```

3. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

4. 配置环境变量：
   ```
   cp .env.example .env
   ```
   编辑 `.env` 文件，设置合适的密钥和配置项。

5. 初始化数据库：
   ```
   python migrate_database.py
   ```

6. 启动服务：
   ```
   python main.py
   ```

   或使用uvicorn：
   ```
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## 项目结构

```
allsmart8/
├── public/                 # 前端静态文件
├── .env.example           # 环境变量示例文件
├── .gitignore             # Git忽略文件
├── README.md              # 项目说明文档
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

## 安全说明

1. **环境变量**：项目使用 `.env` 文件存储敏感配置。请确保 `.env` 文件不在版本控制中（已添加到 `.gitignore`）。

2. **密钥管理**：
   - `ENCRYPTION_KEY`：用于加密API密钥等敏感信息
   - `SECRET_KEY`：用于JWT令牌签名
   - 生产环境中必须使用强随机密钥

3. **数据库加密**：API密钥等敏感信息在数据库中加密存储。

## API文档

启动服务后，可通过以下地址访问API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 开发指南

### 添加新的API配置

1. 通过管理界面或API端点添加新的API配置
2. 敏感信息（如API密钥）会自动加密存储

### 扩展用户权限系统

用户角色权限系统支持层级控制：
- user (基本用户)
- admin (管理员)
- superadmin (超级管理员)

可通过 `auth.check_role()` 装饰器在接口中限制访问权限。

## 部署建议

1. **生产环境配置**：
   - 使用强密钥
   - 配置HTTPS
   - 设置合适的日志级别
   - 使用生产级数据库

2. **反向代理**：
   建议使用Nginx等反向代理服务器部署应用。

3. **容器化部署**：
   可使用Docker进行容器化部署。

## 注意事项

1. 项目默认使用SQLite数据库，生产环境建议使用PostgreSQL或MySQL
2. 前端静态文件位于 `public/` 目录
3. 敏感配置信息应通过环境变量设置，不要硬编码在代码中

## 贡献指南

欢迎提交Issue和Pull Request来改进项目。

## 许可证

请根据实际情况添加合适的开源许可证。
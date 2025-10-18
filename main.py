from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from models import ApiConfig
from schemas import ApiConfigCreate
from crude import create_api_config_crud, get_api_config, get_decrypted_api_key
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from typing import List, Optional
import logging
import httpx
import json
import random
from database import engine, get_db, SessionLocal
from secure_keys import secure_key_manager
# 明确导入Pydantic模型（避免与SQLAlchemy模型混淆）
from schemas import (
    User as PydanticUser,
    UserCreate,
    UserUpdate,
    Device as PydanticDevice,
    DeviceCreate,
    Task as PydanticTask,
    TaskCreate,
    TaskUpdate,
    Admin as PydanticAdmin,
    AdminCreate,
    AdminUpdate,
    ApiConfig as PydanticApiConfig,
    ApiConfigCreate,
    ApiConfigUpdate,
    ApiPermission as PydanticApiPermission,
    ApiPermissionCreate,
    ApiPermissionUpdate,
    Token
)

# 导入SQLAlchemy模型
import models as sqlalchemy_models

from crude import *
from auth import *
from datetime import timedelta
# 导入config_sync模块
import config_sync

# 创建日志记录器
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)
logging.basicConfig(level=logging.INFO)
# 创建数据库表
sqlalchemy_models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AllSmart 智能管理系统", description="用户和管理员后台管理系统", debug=True)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 用户认证端点
@app.post("/api/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# env-preview.py
@app.get("/api/env-preview")
def get_env_preview():
    import os
    return {k: v for k, v in os.environ.items() if k.startswith("API_") or k.startswith("DEEPSEEK_")}

# 用户相关端点
# OAuth2密码认证
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 用户注册端点
@app.post("/register", response_model=dict)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册接口
    """
    try:
        # 检查用户名是否已存在
        existing_user = db.query(User).filter(User.username == user.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="用户名已存在")
        
        # 检查邮箱是否已存在
        existing_email = db.query(User).filter(User.email == user.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="邮箱已存在")
        
        # 创建新用户
        new_user = create_user(db=db, user=user)
        
        return {"message": "注册成功", "user_id": new_user.id}
        
    except HTTPException as e:
        # 确保返回格式一致
        return {"error": e.detail}
    except Exception as e:
        logger.error(f"注册失败: {str(e)}")
        return {"error": "注册失败，请稍后重试"}
# 用户登录端点
@app.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    用户登录接口
    """
    # 认证用户
    user = authenticate_user(db=db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# 获取当前用户信息
@app.get("/users/me", response_model=dict)
async def read_users_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    获取当前登录用户信息
    """
    return {
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at
    }

# 获取所有用户列表（管理员权限）
@app.get("/users", response_model=dict)
async def read_users(skip: int = 0, limit: int = 100, search: str = None, 
                   current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    获取所有用户列表（需要管理员权限）
    """
    # 检查用户是否有管理员权限
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限才能查看用户列表"
        )
    
    users = get_users(db=db, skip=skip, limit=limit, search=search)
    
    return {
        "users": [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            }
            for user in users
        ],
        "total": len(users)
    }

# 获取特定用户信息（管理员权限）
@app.get("/users/{user_id}", response_model=dict)
async def read_user(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    获取特定用户信息（需要管理员权限）
    """
    # 检查用户是否有管理员权限
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限才能查看用户信息"
        )
    
    user = get_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户未找到")
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "updated_at": user.updated_at
    }

# 更新用户信息（管理员权限）
@app.put("/users/{user_id}", response_model=dict)
async def update_user_info(user_id: int, user_update: UserUpdate, 
                         current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    更新用户信息（需要管理员权限）
    """
    # 检查用户是否有管理员权限
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限才能修改用户信息"
        )
    
    updated_user = update_user(db=db, user_id=user_id, user_data=user_update.dict(exclude_unset=True))
    if not updated_user:
        raise HTTPException(status_code=404, detail="用户未找到")
    
    return {"message": "用户信息更新成功"}

# 删除用户（管理员权限）
@app.delete("/users/{user_id}", response_model=dict)
async def delete_user_account(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    删除用户账户（需要管理员权限）
    """
    # 检查用户是否有管理员权限
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限才能删除用户"
        )
    
    success = delete_user(db=db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="用户未找到")
    
    return {"message": "用户删除成功"}
@app.get("/api/users", response_model=List[PydanticUser])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = get_users(db, skip=skip, limit=limit)
    return users

@app.get("/api/users/{user_id}", response_model=PydanticUser)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/api/users", response_model=PydanticUser)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return create_user(db=db, user=user)

@app.put("/api/users/{user_id}", response_model=PydanticUser)
def update_user_endpoint(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    db_user = update_user(db, user_id=user_id, user_data=user.dict(exclude_unset=True))
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.delete("/api/users/{user_id}")
def delete_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    if delete_user(db, user_id=user_id):
        return {"message": "User deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found")

# 设备相关端点
@app.get("/api/devices", response_model=List[PydanticDevice])
def read_devices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    devices = get_devices(db, skip=skip, limit=limit)
    return devices

@app.get("/api/devices/{device_id}", response_model=PydanticDevice)
def read_device(device_id: int, db: Session = Depends(get_db)):
    db_device = get_device(db, device_id=device_id)
    if db_device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return db_device

@app.post("/api/devices", response_model=PydanticDevice)
def create_device(device: DeviceCreate, db: Session = Depends(get_db)):
    return create_device(db=db, device=device)

@app.put("/api/devices/{device_id}", response_model=PydanticDevice)
def update_device_endpoint(device_id: int, device: DeviceUpdate, db: Session = Depends(get_db)):
    db_device = update_device(db, device_id=device_id, device_data=device.dict(exclude_unset=True))
    if db_device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return db_device

@app.delete("/api/devices/{device_id}")
def delete_device_endpoint(device_id: int, db: Session = Depends(get_db)):
    if delete_device(db, device_id=device_id):
        return {"message": "Device deleted successfully"}
    raise HTTPException(status_code=404, detail="Device not found")

# 任务相关端点
@app.get("/api/tasks", response_model=List[PydanticTask])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tasks = get_tasks(db, skip=skip, limit=limit)
    return tasks

@app.get("/api/tasks/{task_id}", response_model=PydanticTask)
def read_task(task_id: int, db: Session = Depends(get_db)):
    db_task = get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@app.post("/api/tasks", response_model=PydanticTask)
def create_task_endpoint(task: TaskCreate, db: Session = Depends(get_db)):
    return create_task(db=db, task=task)

@app.put("/api/tasks/{task_id}", response_model=PydanticTask)
def update_task_endpoint(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    db_task = update_task(db, task_id=task_id, task_data=task.dict(exclude_unset=True))
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@app.delete("/api/tasks/{task_id}")
def delete_task_endpoint(task_id: int, db: Session = Depends(get_db)):
    if delete_task(db, task_id=task_id):
        return {"message": "Task deleted successfully"}
    raise HTTPException(status_code=404, detail="Task not found")

# 管理员相关端点
@app.get("/api/admins", response_model=List[PydanticAdmin])
def read_admins(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    admins = get_admins(db, skip=skip, limit=limit)
    return admins

@app.get("/api/admins/{admin_id}", response_model=PydanticAdmin)
def read_admin(admin_id: int, db: Session = Depends(get_db)):
    db_admin = get_admin(db, admin_id=admin_id)
    if db_admin is None:
        raise HTTPException(status_code=404, detail="Admin not found")
    return db_admin

@app.post("/api/admins", response_model=PydanticAdmin)
def create_admin_endpoint(admin: AdminCreate, db: Session = Depends(get_db)):
    db_admin = get_admin_by_username(db, username=admin.username)
    if db_admin:
        raise HTTPException(status_code=400, detail="Username already registered")
    return create_admin(db=db, admin=admin)

@app.put("/api/admins/{admin_id}", response_model=PydanticAdmin)
def update_admin_endpoint(admin_id: int, admin: AdminUpdate, db: Session = Depends(get_db)):
    db_admin = update_admin(db, admin_id=admin_id, admin_data=admin.dict(exclude_unset=True))
    if db_admin is None:
        raise HTTPException(status_code=404, detail="Admin not found")
    return db_admin

@app.delete("/api/admins/{admin_id}")
def delete_admin_endpoint(admin_id: int, db: Session = Depends(get_db)):
    if delete_admin(db, admin_id=admin_id):
        return {"message": "Admin deleted successfully"}
    raise HTTPException(status_code=404, detail="Admin not found")

# API配置相关端点
@app.get("/api/api-configs", response_model=List[PydanticApiConfig])
def read_api_configs(skip: int = 0, limit: int = 100, search: str = None, db: Session = Depends(get_db)):
    api_configs = get_api_configs(db, skip=skip, limit=limit, search=search)
    return api_configs

@app.get("/api/api-configs/{api_config_id}", response_model=PydanticApiConfig)
def read_api_config(api_config_id: int, db: Session = Depends(get_db)):
    db_api_config = get_api_config(db, api_config_id=api_config_id)
    if db_api_config is None:
        raise HTTPException(status_code=404, detail="API config not found")
    return db_api_config

# 更新create_api_config_endpoint函数
@app.post("/api/api-configs", response_model=PydanticApiConfig)
def create_api_config_endpoint(api_config: ApiConfigCreate, db: Session = Depends(get_db)):
    try:
        db_api_config = create_api_config_crud(db, api_config)
        return db_api_config
    except Exception as e:
        logger.error(f"Failed to create API config: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.put("/api/api-configs/{api_config_id}", response_model=PydanticApiConfig)
def update_api_config(api_config_id: int, api_config: ApiConfigUpdate, db: Session = Depends(get_db)):
    db_api_config = update_api_config(db, api_config_id=api_config_id, api_config_data=api_config)
    if db_api_config is None:
        raise HTTPException(status_code=404, detail="API config not found")
    return db_api_config

@app.delete("/api/api-configs/{api_config_id}")
def delete_api_config_endpoint(api_config_id: int, db: Session = Depends(get_db)):
    if delete_api_config(db, api_config_id=api_config_id):
        return {"message": "API config deleted successfully"}
    raise HTTPException(status_code=404, detail="API config not found")

# 添加AI服务调用端点

@app.post("/api/ai/chat")
async def ai_chat(message: str, db: Session = Depends(get_db)):
    # 获取默认的AI API配置（例如 DeepSeek 或 OpenAI）
    api_config = db.query(ApiConfig).filter(
        ApiConfig.name == "DeepSeek",
        ApiConfig.is_active == True
    ).first()

    if not api_config:
        raise HTTPException(status_code=404, detail="AI API配置未找到")

    # 解密API密钥
    api_key = get_decrypted_api_key(db, api_config.id)
    if not api_key:
        raise HTTPException(status_code=500, detail="无法解密API密钥")

    # 构造请求
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "messages": [{"role": "user", "content": message}],
        "model": "deepseek-chat"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(api_config.endpoint, headers=headers, json=payload)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    result = response.json()
    return {"response": result["choices"][0]["message"]["content"]}

# 添加AI服务调用端点
from pydantic import BaseModel

class ChatMessage(BaseModel):
    message: str

@app.post("/api/ai/chat")
async def ai_chat(chat_message: ChatMessage, db: Session = Depends(get_db)):
    message = chat_message.message
    
    # 获取默认的AI API配置（例如 DeepSeek 或 OpenAI）
    api_config = db.query(ApiConfig).filter(
        ApiConfig.name == "DeepSeek",
        ApiConfig.is_active == True
    ).first()

    if not api_config:
        raise HTTPException(status_code=404, detail="AI API配置未找到")

    # 解密API密钥
    api_key = get_decrypted_api_key(db, api_config.id)
    if not api_key:
        raise HTTPException(status_code=500, detail="无法解密API密钥")

    # 构造请求
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "messages": [{"role": "user", "content": message}],
        "model": "deepseek-chat"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(api_config.endpoint, headers=headers, json=payload)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    result = response.json()
    return {"response": result["choices"][0]["message"]["content"]}
@app.post("/api/ai/chat")
async def ai_chat(message: str):
    return {"response": "这是AI的模拟回复，实际API尚未连接。"}

# API权限相关端点
@app.get("/api/api-permissions", response_model=List[PydanticApiPermission])
def read_api_permissions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    api_permissions = get_api_permissions(db, skip=skip, limit=limit)
    return api_permissions

@app.get("/api/api-permissions/{api_permission_id}", response_model=PydanticApiPermission)
def read_api_permission(api_permission_id: int, db: Session = Depends(get_db)):
    db_api_permission = get_api_permission(db, api_permission_id=api_permission_id)
    if db_api_permission is None:
        raise HTTPException(status_code=404, detail="API permission not found")
    return db_api_permission

@app.post("/api/api-permissions", response_model=PydanticApiPermission)
def create_api_permission_endpoint(api_permission: ApiPermissionCreate, db: Session = Depends(get_db)):
    return create_api_permission(db=db, api_permission=api_permission)

@app.put("/api/api-permissions/{api_permission_id}", response_model=PydanticApiPermission)
def update_api_permission_endpoint(api_permission_id: int, api_permission: ApiPermissionUpdate, db: Session = Depends(get_db)):
    db_api_permission = update_api_permission(db, api_permission_id=api_permission_id, api_permission_data=api_permission.dict(exclude_unset=True))
    if db_api_permission is None:
        raise HTTPException(status_code=404, detail="API permission not found")
    return db_api_permission

@app.delete("/api/api-permissions/{api_permission_id}")
def delete_api_permission_endpoint(api_permission_id: int, db: Session = Depends(get_db)):
    if delete_api_permission(db, api_permission_id=api_permission_id):
        return {"message": "API permission deleted successfully"}
    raise HTTPException(status_code=404, detail="API permission not found")

# 用户偏好设置相关端点
@app.get("/api/user-preferences/{user_id}")
def read_user_preferences(user_id: int, preference_type: Optional[str] = None, db: Session = Depends(get_db)):
    preferences = get_user_preferences(db, user_id=user_id, preference_type=preference_type)
    return preferences

@app.post("/api/user-preferences")
def create_user_preference_endpoint(user_preference: UserPreferenceCreate, db: Session = Depends(get_db)):
    return create_user_preference(db=db, user_preference=user_preference)

@app.put("/api/user-preferences/{user_id}/{preference_type}/{preference_name}")
def update_user_preference_endpoint(
    user_id: int, 
    preference_type: str, 
    preference_name: str, 
    value: dict,
    db: Session = Depends(get_db)
):
    return update_user_preference(db, user_id, preference_type, preference_name, value)

@app.delete("/api/user-preferences/{user_id}/{preference_type}/{preference_name}")
def delete_user_preference_endpoint(
    user_id: int, 
    preference_type: str, 
    preference_name: str,
    db: Session = Depends(get_db)
):
    if delete_user_preference(db, user_id, preference_type, preference_name):
        return {"message": "User preference deleted successfully"}
    raise HTTPException(status_code=404, detail="User preference not found")

# 根目录重定向到管理页面
from fastapi.responses import RedirectResponse

@app.get("/")
def redirect_to_admin():
    return RedirectResponse(url="/admin.html")

# 静态文件服务
# 使用 public 目录作为静态文件服务
app.mount("/", StaticFiles(directory="public", html=True), name="static")

@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    logger.error(f"Exception occurred: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error"}
    )

if __name__ == "__main__":
    # 启动时从 .env 同步到数据库
    config_sync.sync_db_from_env()
    
    # 使用 uvicorn 运行应用（正确方式）
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
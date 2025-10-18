from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

# 用户相关
class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)

# 设备相关
class DeviceBase(BaseModel):
    device_id: str
    name: str
    ip_address: str
    mac_address: str
    status: Optional[str] = "offline"

class DeviceCreate(DeviceBase):
    pass

class DeviceUpdate(DeviceBase):
    pass

class Device(DeviceBase):
    id: int
    connected_at: datetime
    owner_id: int
    
    model_config = ConfigDict(from_attributes=True)

# 任务相关
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    completed: Optional[bool] = False

class TaskCreate(TaskBase):
    pass

class TaskUpdate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    owner_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# 管理员相关
class AdminBase(BaseModel):
    username: str
    role: Optional[str] = "admin"

class AdminCreate(AdminBase):
    password: str

class AdminUpdate(AdminBase):
    password: Optional[str] = None

class Admin(AdminBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)

# API配置相关
class ApiConfigBase(BaseModel):
    name: str
    endpoint: str
    method: Optional[str] = "GET"
    is_active: Optional[bool] = True
    is_public: Optional[bool] = False
    description: Optional[str] = None
    # 新增字段
    auth_type: Optional[str] = None
    provider: Optional[str] = None
    category: Optional[str] = None
    max_requests: Optional[int] = 1000
    priority: Optional[int] = 2
    # 音乐特定字段
    music_genres: Optional[str] = None
    music_quality: Optional[str] = None
    music_region: Optional[str] = None

class ApiConfigCreate(ApiConfigBase):
    # 创建时可以包含明文密钥，但不会存储明文
    api_key: Optional[str] = None

class ApiConfigUpdate(ApiConfigBase):
    # 更新时可以包含明文密钥，但不会存储明文
    api_key: Optional[str] = None

class ApiConfig(ApiConfigBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    # 不在响应中包含加密的密钥
    
    model_config = ConfigDict(from_attributes=True)

# API权限相关
class ApiPermissionBase(BaseModel):
    api_config_id: int
    user_id: int
    can_access: Optional[bool] = False
    can_modify: Optional[bool] = False

class ApiPermissionCreate(ApiPermissionBase):
    pass

class ApiPermissionUpdate(ApiPermissionBase):
    pass

class ApiPermission(ApiPermissionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)

# 用户偏好设置
class UserPreferenceBase(BaseModel):
    preference_type: str
    preference_name: str
    value: Dict[str, Any]

class UserPreferenceCreate(UserPreferenceBase):
    pass

class UserPreferenceUpdate(UserPreferenceBase):
    pass

class UserPreference(UserPreferenceBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)

# 生物识别数据
class BiometricDataBase(BaseModel):
    type: str
    data: Dict[str, Any]
    is_active: Optional[bool] = True

class BiometricDataCreate(BiometricDataBase):
    pass

class BiometricDataUpdate(BiometricDataBase):
    pass

class BiometricData(BiometricDataBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)

# 认证相关
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str
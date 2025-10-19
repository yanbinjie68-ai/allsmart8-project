# models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
from passlib.context import CryptContext
import datetime  # ✅ 已经导入
created_at = Column(DateTime, default=func.now())
updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    """
    用户模型
    
    代表系统中的普通用户，包含基本信息、认证信息和关联数据。
    """
    __tablename__ = "users"
    
    # 基本字段
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 添加索引以提高查询性能
    __table_args__ = (
        Index('idx_users_role', 'role'),
        Index('idx_users_created_at', 'created_at'),
    )
    
    # 关系定义
    devices = relationship("Device", back_populates="owner")
    tasks = relationship("Task", back_populates="owner")
    preferences = relationship("UserPreference", back_populates="user")
    biometric_data = relationship("BiometricData", back_populates="user")
    
    def verify_password(self, plain_password: str) -> bool:
        """
        验证密码
        
        Args:
            plain_password (str): 明文密码
            
        Returns:
            bool: 密码正确返回True，否则返回False
        """
        return pwd_context.verify(plain_password, self.hashed_password)
    
    def set_password(self, password: str):
        """
        设置用户密码（哈希处理）
        
        Args:
            password (str): 明文密码
        """
        self.hashed_password = pwd_context.hash(password)

class Device(Base):
    """
    设备模型
    
    代表用户关联的设备信息，包括网络地址、状态等。
    """
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, unique=True, index=True)
    name = Column(String)
    ip_address = Column(String)
    mac_address = Column(String)
    status = Column(String, default="offline")  # online, offline
    connected_at = Column(DateTime(timezone=True), server_default=func.now())
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # 关系定义
    owner = relationship("User", back_populates="devices")

class Task(Base):
    """
    任务模型
    
    代表用户的任务信息，包括标题、描述、截止日期等。
    """
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    completed = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系定义
    owner = relationship("User", back_populates="tasks")

class Admin(Base):
    """
    管理员模型
    
    代表系统管理员，具有管理用户、设备等高级权限。
    """
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="admin")  # admin, superadmin
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    def verify_password(self, plain_password: str) -> bool:
        """
        验证管理员密码
        
        Args:
            plain_password (str): 明文密码
            
        Returns:
            bool: 密码正确返回True，否则返回False
        """
        return pwd_context.verify(plain_password, self.hashed_password)
    
    def set_password(self, password: str):
        """
        设置管理员密码（哈希处理）
        
        Args:
            password (str): 明文密码
        """
        self.hashed_password = pwd_context.hash(password)


class ApiConfig(Base):
    """
    API配置模型
    
    存储外部API的配置信息，包括端点、认证方式、加密密钥等。
    敏感信息（如API密钥）会被加密存储。
    """
    __tablename__ = "api_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)
    endpoint = Column(String(255))
    method = Column(String(10))
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
    description = Column(Text, nullable=True)
    
    # 安全字段用于存储加密的API密钥和其他认证信息
    auth_type = Column(String(20), nullable=True)  # apiKey, oauth, bearer等
    encrypted_key = Column(Text, nullable=True)    # 加密的API密钥
    provider = Column(String(100), nullable=True)  # API提供商
    category = Column(String(50), nullable=True)   # API类别
    max_requests = Column(Integer, default=1000)   # 每小时最大请求数
    priority = Column(Integer, default=2)          # 优先级
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # 音乐特定字段
    music_genres = Column(Text, nullable=True)     # 支持的音乐类型
    music_quality = Column(String(20), nullable=True)  # 音质选项 (low, medium, high, lossless)
    music_region = Column(String(10), nullable=True)   # 地区代码 (如: US, CN, JP)
    
    # 关系定义
    permissions = relationship("ApiPermission", back_populates="api_config")

class ApiPermission(Base):
    """
    API权限模型
    
    定义用户对特定API配置的访问权限。
    """
    __tablename__ = "api_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    api_config_id = Column(Integer, ForeignKey("api_configs.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    can_access = Column(Boolean, default=False)
    can_modify = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # 关系定义
    api_config = relationship("ApiConfig", back_populates="permissions")
    user = relationship("User")

class UserPreference(Base):
    """
    用户偏好设置模型
    
    存储用户的个性化设置，以JSON格式保存各种偏好配置。
    """
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    preference_type = Column(String)  # api, device, system
    preference_name = Column(String)
    value = Column(JSON)  # 存储JSON格式的偏好设置
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # 关系定义
    user = relationship("User", back_populates="preferences")

class BiometricData(Base):
    """
    生物识别数据模型
    
    存储用户的生物识别信息，如指纹、面部识别等数据。
    所有数据都以JSON格式存储，并可以标记为激活或未激活状态。
    """
    __tablename__ = "biometric_data"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String)  # face, fingerprint, voice
    data = Column(JSON)  # 存储生物识别数据
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # 关系定义
    user = relationship("User", back_populates="biometric_data")
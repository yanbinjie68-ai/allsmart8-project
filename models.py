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
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 添加索引
    __table_args__ = (
        Index('idx_users_role', 'role'),
        Index('idx_users_created_at', 'created_at'),
    )
    # 关系
    devices = relationship("Device", back_populates="owner")
    tasks = relationship("Task", back_populates="owner")
    preferences = relationship("UserPreference", back_populates="user")
    biometric_data = relationship("BiometricData", back_populates="user")
    
    
    def verify_password(self, plain_password):
        return pwd_context.verify(plain_password, self.hashed_password)
    
    def set_password(self, password):
        self.hashed_password = pwd_context.hash(password)

class Device(Base):
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, unique=True, index=True)
    name = Column(String)
    ip_address = Column(String)
    mac_address = Column(String)
    status = Column(String, default="offline")  # online, offline
    connected_at = Column(DateTime(timezone=True), server_default=func.now())
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # 关系
    owner = relationship("User", back_populates="devices")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    completed = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    owner = relationship("User", back_populates="tasks")

class Admin(Base):
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="admin")  # admin, superadmin
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    def verify_password(self, plain_password):
        return pwd_context.verify(plain_password, self.hashed_password)
    
    def set_password(self, password):
        self.hashed_password = pwd_context.hash(password)


class ApiConfig(Base):
    __tablename__ = "api_configs"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)
    endpoint = Column(String(255))
    method = Column(String(10))
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
    description = Column(Text, nullable=True)
    # 添加安全字段用于存储加密的API密钥和其他认证信息
    auth_type = Column(String(20), nullable=True)  # apiKey, oauth, bearer等
    encrypted_key = Column(Text, nullable=True)    # 加密的API密钥
    provider = Column(String(100), nullable=True)  # API提供商
    category = Column(String(50), nullable=True)   # API类别
    max_requests = Column(Integer, default=1000)   # 每小时最大请求数
    priority = Column(Integer, default=2)          # 优先级
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 音乐特定字段
    music_genres = Column(Text, nullable=True)     # 支持的音乐类型
    music_quality = Column(String(20), nullable=True)  # 音质选项 (low, medium, high, lossless)
    music_region = Column(String(10), nullable=True)   # 地区代码 (如: US, CN, JP)
    
    # 关系
    permissions = relationship("ApiPermission", back_populates="api_config")

class ApiPermission(Base):
    __tablename__ = "api_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    api_config_id = Column(Integer, ForeignKey("api_configs.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    can_access = Column(Boolean, default=False)
    can_modify = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # 关系
    api_config = relationship("ApiConfig", back_populates="permissions")
    user = relationship("User")

class UserPreference(Base):
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    preference_type = Column(String)  # api, device, system
    preference_name = Column(String)
    value = Column(JSON)  # 存储JSON格式的偏好设置
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # 关系
    user = relationship("User", back_populates="preferences")

class BiometricData(Base):
    __tablename__ = "biometric_data"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String)  # face, fingerprint, voice
    data = Column(JSON)  # 存储生物识别数据
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # 关系
    user = relationship("User", back_populates="biometric_data")
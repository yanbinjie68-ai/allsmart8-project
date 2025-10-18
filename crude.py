import uuid
import datetime
from typing import Optional
from sqlalchemy.orm import Session
from models import User, Device, Task, Admin, ApiConfig, ApiPermission, UserPreference, BiometricData
from schemas import (
    UserCreate, UserUpdate, DeviceCreate, DeviceUpdate, TaskCreate, TaskUpdate,
    AdminCreate, AdminUpdate, ApiConfigCreate, ApiConfigUpdate, ApiPermissionCreate, ApiPermissionUpdate,
    UserPreferenceCreate, UserPreferenceUpdate, BiometricDataCreate, BiometricDataUpdate
)
from passlib.context import CryptContext
from secure_keys import secure_key_manager
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100, search: str = None):
    query = db.query(User)
    if search:
        query = query.filter(
            User.username.contains(search) | 
            User.email.contains(search) |
            User.full_name.contains(search)
        )
    return query.offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_data: dict):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        for key, value in user_data.items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False

def get_device(db: Session, device_id: int):
    return db.query(Device).filter(Device.id == device_id).first()

def get_devices(db: Session, owner_id: int = None):
    query = db.query(Device)
    if owner_id:
        query = query.filter(Device.owner_id == owner_id)
    return query.all()

def create_device(db: Session, device: DeviceCreate, owner_id: int):
    db_device = Device(**device.dict(), owner_id=owner_id)
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device

def update_device(db: Session, device_id: int, device_data: dict):
    db_device = db.query(Device).filter(Device.id == device_id).first()
    if db_device:
        for key, value in device_data.items():
            setattr(db_device, key, value)
        db.commit()
        db.refresh(db_device)
    return db_device

def delete_device(db: Session, device_id: int):
    db_device = db.query(Device).filter(Device.id == device_id).first()
    if db_device:
        db.delete(db_device)
        db.commit()
        return True
    return False

def get_task(db: Session, task_id: int):
    return db.query(Task).filter(Task.id == task_id).first()

def get_tasks(db: Session, owner_id: int):
    return db.query(Task).filter(Task.owner_id == owner_id).all()

def create_task(db: Session, task: TaskCreate, owner_id: int):
    db_task = Task(**task.dict(), owner_id=owner_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, task_id: int, task_data: dict):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task:
        for key, value in task_data.items():
            setattr(db_task, key, value)
        db.commit()
        db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task:
        db.delete(db_task)
        db.commit()
        return True
    return False

def get_admin(db: Session, admin_id: int):
    return db.query(Admin).filter(Admin.id == admin_id).first()

def get_admin_by_username(db: Session, username: str):
    return db.query(Admin).filter(Admin.username == username).first()

def get_admins(db: Session, skip: int = 0, limit: int = 100, search: str = None):
    query = db.query(Admin)
    if search:
        query = query.filter(Admin.username.contains(search))
    return query.offset(skip).limit(limit).all()

def create_admin(db: Session, admin: AdminCreate):
    db_admin = Admin(**admin.dict())
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin

def update_admin(db: Session, admin_id: int, admin_data: dict):
    db_admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if db_admin:
        for key, value in admin_data.items():
            setattr(db_admin, key, value)
        db.commit()
        db.refresh(db_admin)
    return db_admin

def delete_admin(db: Session, admin_id: int):
    db_admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if db_admin:
        db.delete(db_admin)
        db.commit()
        return True
    return False

def get_api_config(db: Session, api_config_id: int):
    return db.query(ApiConfig).filter(ApiConfig.id == api_config_id).first()
def get_api_configs(db: Session, skip: int = 0, limit: int = 100, search: str = None):
    query = db.query(ApiConfig)
    if search:
        query = query.filter(ApiConfig.name.contains(search) | ApiConfig.endpoint.contains(search))
    return query.offset(skip).limit(limit).all()

def create_api_config_crud(db: Session, api_config: ApiConfigCreate):
    try:
        # 创建数据库对象，但不直接存储API密钥
        db_api_config = ApiConfig(
            name=api_config.name,
            endpoint=api_config.endpoint,
            method=api_config.method,
            is_active=api_config.is_active,
            is_public=api_config.is_public,
            description=api_config.description,
            auth_type=api_config.auth_type,
            provider=api_config.provider,
            category=api_config.category,
            max_requests=api_config.max_requests,
            priority=api_config.priority,
            music_genres=api_config.music_genres,
            music_quality=api_config.music_quality,
            music_region=api_config.music_region
        )
        
        # 如果提供了API密钥，进行加密并存储
        if api_config.api_key:
            encrypted_key = secure_key_manager.encrypt_key(api_config.api_key)
            db_api_config.encrypted_key = encrypted_key
        
        db.add(db_api_config)
        db.commit()
        db.refresh(db_api_config)
        return db_api_config
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create API config: {e}")
        raise HTTPException(status_code=500, detail="Failed to save API config")

def update_api_config(db: Session, api_config_id: int, api_config_data: ApiConfigUpdate):
    db_api_config = get_api_config(db, api_config_id=api_config_id)
    if db_api_config is None:
        return None
    
    # 更新字段
    update_data = api_config_data.dict(exclude_unset=True)
    
    # 如果提供了新的API密钥，则加密并更新
    if 'api_key' in update_data and update_data['api_key']:
        db_api_config.encrypted_key = secure_key_manager.encrypt_key(update_data['api_key'])
        del update_data['api_key']  # 从更新数据中移除明文密钥
    
    # 更新其他字段
    for key, value in update_data.items():
        setattr(db_api_config, key, value)
    
    try:
        db.commit()
        db.refresh(db_api_config)
        return db_api_config
    except Exception as e:
        db.rollback()
        raise e

# 添加一个函数用于获取解密的API密钥
def get_decrypted_api_key(db: Session, api_config_id: int) -> Optional[str]:
    db_api_config = get_api_config(db, api_config_id=api_config_id)
    if db_api_config and db_api_config.encrypted_key:
        return secure_key_manager.decrypt_key(db_api_config.encrypted_key)
    return None

def delete_api_config(db: Session, api_config_id: int):
    db_api_config = db.query(ApiConfig).filter(ApiConfig.id == api_config_id).first()
    if db_api_config:
        db.delete(db_api_config)
        db.commit()
        return True
    return False

def get_api_permission(db: Session, api_permission_id: int):
    return db.query(ApiPermission).filter(ApiPermission.id == api_permission_id).first()

def get_api_permissions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(ApiPermission).offset(skip).limit(limit).all()

def create_api_permission(db: Session, api_permission: ApiPermissionCreate):
    db_api_permission = ApiPermission(**api_permission.dict())
    db.add(db_api_permission)
    db.commit()
    db.refresh(db_api_permission)
    return db_api_permission

def update_api_permission(db: Session, api_permission_id: int, api_permission_data: dict):
    db_api_permission = db.query(ApiPermission).filter(ApiPermission.id == api_permission_id).first()
    if db_api_permission:
        for key, value in api_permission_data.items():
            setattr(db_api_permission, key, value)
        db.commit()
        db.refresh(db_api_permission)
    return db_api_permission

def delete_api_permission(db: Session, api_permission_id: int):
    db_api_permission = db.query(ApiPermission).filter(ApiPermission.id == api_permission_id).first()
    if db_api_permission:
        db.delete(db_api_permission)
        db.commit()
        return True
    return False

def get_user_preference(db: Session, user_id: int, preference_type: str, preference_name: str):
    return db.query(UserPreference).filter(
        UserPreference.user_id == user_id,
        UserPreference.preference_type == preference_type,
        UserPreference.preference_name == preference_name
    ).first()

def get_user_preferences(db: Session, user_id: int, preference_type: str = None):
    query = db.query(UserPreference).filter(UserPreference.user_id == user_id)
    if preference_type:
        query = query.filter(UserPreference.preference_type == preference_type)
    return query.all()

def create_user_preference(db: Session, user_preference: UserPreferenceCreate):
    db_preference = UserPreference(**user_preference.dict())
    db.add(db_preference)
    db.commit()
    db.refresh(db_preference)
    return db_preference

def update_user_preference(db: Session, user_id: int, preference_type: str, preference_name: str, preference_data: dict):
    db_preference = db.query(UserPreference).filter(
        UserPreference.user_id == user_id,
        UserPreference.preference_type == preference_type,
        UserPreference.preference_name == preference_name
    ).first()
    if db_preference:
        db_preference.value = preference_data
        db_preference.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_preference)
    return db_preference

def delete_user_preference(db: Session, user_id: int, preference_type: str, preference_name: str):
    db_preference = db.query(UserPreference).filter(
        UserPreference.user_id == user_id,
        UserPreference.preference_type == preference_type,
        UserPreference.preference_name == preference_name
    ).first()
    if db_preference:
        db.delete(db_preference)
        db.commit()
        return True
    return False

def get_biometric_data(db: Session, user_id: int, data_type: str):
    return db.query(BiometricData).filter(
        BiometricData.user_id == user_id,
        BiometricData.type == data_type
    ).first()

def get_biometric_data_all(db: Session, user_id: int):
    return db.query(BiometricData).filter(BiometricData.user_id == user_id).all()

def create_biometric_data(db: Session, biometric_data: BiometricDataCreate):
    db_biometric = BiometricData(**biometric_data.dict())
    db.add(db_biometric)
    db.commit()
    db.refresh(db_biometric)
    return db_biometric

def update_biometric_data(db: Session, user_id: int, data_type: str, biometric_data: dict):
    db_biometric = db.query(BiometricData).filter(
        BiometricData.user_id == user_id,
        BiometricData.type == data_type
    ).first()
    if db_biometric:
        db_biometric.data = biometric_data
        db_biometric.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_biometric)
    return db_biometric

def delete_biometric_data(db: Session, user_id: int, data_type: str):
    db_biometric = db.query(BiometricData).filter(
        BiometricData.user_id == user_id,
        BiometricData.type == data_type
    ).first()
    if db_biometric:
        db.delete(db_biometric)
        db.commit()
        return True
    return False
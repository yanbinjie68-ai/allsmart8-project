# api.py - 重构后的版本
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from crude import (
    create_user, get_users, update_user, delete_user,
    create_admin, get_admins, update_admin, delete_admin,
    create_api_config_crud, get_api_configs, update_api_config, delete_api_config,
    get_api_config
)
from schemas import (
    UserCreate, UserUpdate, User, 
    AdminCreate, AdminUpdate, Admin,
    ApiConfigCreate, ApiConfigUpdate, ApiConfig
)

router = APIRouter()

# 用户管理路由
@router.post("/users", response_model=User)
def create_user_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)

@router.get("/users", response_model=list[User])
def read_users(skip: int = 0, limit: int = 100, search: str = None, db: Session = Depends(get_db)):
    return get_users(db, skip=skip, limit=limit, search=search)

@router.put("/users/{user_id}", response_model=User)
def update_user_endpoint(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    return update_user(db, user_id, user_data.dict())

@router.delete("/users/{user_id}")
def delete_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    if not delete_user(db, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

# 系统管理路由
@router.post("/admins", response_model=Admin)
def create_admin_endpoint(admin: AdminCreate, db: Session = Depends(get_db)):
    return create_admin(db, admin)

@router.get("/admins", response_model=list[Admin])
def read_admins(skip: int = 0, limit: int = 100, search: str = None, db: Session = Depends(get_db)):
    return get_admins(db, skip=skip, limit=limit, search=search)

@router.put("/admins/{admin_id}", response_model=Admin)
def update_admin_endpoint(admin_id: int, admin_data: AdminUpdate, db: Session = Depends(get_db)):
    return update_admin(db, admin_id, admin_data.dict())

@router.delete("/admins/{admin_id}")
def delete_admin_endpoint(admin_id: int, db: Session = Depends(get_db)):
    if not delete_admin(db, admin_id):
        raise HTTPException(status_code=404, detail="Admin not found")
    return {"message": "Admin deleted successfully"}

# API配置管理路由
@router.post("/api-configs", response_model=ApiConfig)
def create_api_config_endpoint(api_config: ApiConfigCreate, db: Session = Depends(get_db)):
    return create_api_config_crud(db, api_config)

@router.get("/api-configs", response_model=list[ApiConfig])
def read_api_configs(skip: int = 0, limit: int = 100, search: str = None, db: Session = Depends(get_db)):
    return get_api_configs(db, skip=skip, limit=limit, search=search)


# ... existing code ...
@router.put("/api-configs/{config_id}", response_model=ApiConfig)
def update_api_config_endpoint(config_id: int, api_config: ApiConfigUpdate, db: Session = Depends(get_db)):
    # 获取现有配置
    existing_config = get_api_config(db, config_id)
    if not existing_config:
        raise HTTPException(status_code=404, detail="API config not found")
    
    # 更新配置
    updated_config = update_api_config(db, config_id, api_config)
    return updated_config

@router.delete("/api-configs/{config_id}")
def delete_api_config_endpoint(config_id: int, db: Session = Depends(get_db)):
    if not delete_api_config(db, config_id):
        raise HTTPException(status_code=404, detail="API config not found")
    return {"message": "API config deleted successfully"}
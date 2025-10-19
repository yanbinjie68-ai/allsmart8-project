"""
认证模块

该模块负责用户认证、密码验证和JWT令牌管理。
包含用户密码哈希、JWT令牌生成和验证等功能。
"""
import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db
from crude import get_user, get_admin
from schemas import TokenData
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# JWT配置
# 注意：在生产环境中，这些值必须通过环境变量设置，不能使用默认值
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-jwt-key-here-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2密码流
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证明文密码与哈希密码是否匹配
    
    Args:
        plain_password (str): 明文密码
        hashed_password (str): 哈希密码
        
    Returns:
        bool: 密码匹配返回True，否则返回False
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    对密码进行哈希处理
    
    Args:
        password (str): 明文密码
        
    Returns:
        str: 哈希后的密码
    """
    return pwd_context.hash(password)

def authenticate_user(db: Session, username: str, password: str):
    """
    验证用户凭据
    
    Args:
        db (Session): 数据库会话
        username (str): 用户名
        password (str): 密码
        
    Returns:
        User对象或False: 验证成功返回User对象，失败返回False
    """
    user = get_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def authenticate_admin(db: Session, username: str, password: str):
    """
    验证管理员凭据
    
    Args:
        db (Session): 数据库会话
        username (str): 管理员用户名
        password (str): 密码
        
    Returns:
        Admin对象或False: 验证成功返回Admin对象，失败返回False
    """
    admin = get_admin(db, username)
    if not admin or not verify_password(password, admin.hashed_password):
        return False
    return admin

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建访问令牌
    
    Args:
        data (dict): 要编码到令牌中的数据
        expires_delta (Optional[timedelta]): 令牌过期时间
        
    Returns:
        str: JWT访问令牌
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    获取当前认证用户
    
    Args:
        token (str): JWT访问令牌
        db (Session): 数据库会话
        
    Returns:
        User或Admin对象: 当前认证的用户或管理员
        
    Raises:
        HTTPException: 令牌无效或用户不存在时抛出401错误
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username, role=role)
    except JWTError:
        raise credentials_exception
    # 根据角色获取用户或管理员
    user = get_user(db, username=token_data.username) if token_data.role == "user" else get_admin(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

def check_role(required_role: str):
    """
    检查用户角色权限的装饰器函数
    
    Args:
        required_role (str): 所需的最低角色权限
        
    Returns:
        function: 角色检查装饰器
    """
    def role_checker(current_user):
        # 角色层级定义，数字越大权限越高
        role_hierarchy = {
            "user": 1,
            "admin": 2,
            "superadmin": 3
        }
        
        user_role = current_user.role
        # 检查用户角色是否满足所需权限
        if role_hierarchy.get(user_role, 0) < role_hierarchy.get(required_role, 0):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker
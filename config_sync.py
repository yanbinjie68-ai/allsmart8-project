"""
配置同步模块

该模块负责在环境变量(.env文件)和数据库之间同步API配置信息。
支持从数据库同步到.env文件，以及从.env文件初始化数据库。
"""
import os
from dotenv import load_dotenv, find_dotenv
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import ApiConfig
from database import get_db
from secure_keys import secure_key_manager

def sync_env_from_db():
    """
    从数据库同步API配置到.env文件
    
    该函数读取数据库中的所有API配置，并将其写入.env文件。
    每个配置项将生成两个环境变量：
    1. {NAME}_ENDPOINT - API端点URL
    2. {NAME}_API_KEY - 加密的API密钥（如果存在）
    
    注意：此操作会覆盖.env文件中的现有内容。
    """
    env_path = find_dotenv()
    if not env_path:
        raise FileNotFoundError(".env file not found")

    try:
        # 获取所有API配置
        db = next(get_db())
        configs = db.query(ApiConfig).all()

        # 构建新的.env内容
        lines = []
        for config in configs:
            # 将配置名称转换为大写并用下划线替换空格
            key = config.name.upper().replace(" ", "_")
            endpoint_var = f"{key}_ENDPOINT"
            key_var = f"{key}_API_KEY"

            # 添加端点配置
            lines.append(f"{endpoint_var}={config.endpoint}")
            
            # 如果存在加密的API密钥，则解密并添加
            if config.encrypted_key:
                decrypted_key = secure_key_manager.decrypt_key(config.encrypted_key)
                lines.append(f"{key_var}={decrypted_key}")

        # 写入.env文件
        with open(env_path, 'w') as f:
            f.write('\n'.join(lines))
        print("✅ Config synced to .env")
    except Exception as e:
        print(f"❌ Error syncing config to .env: {e}")

def sync_db_from_env():
    """
    从.env文件同步API配置到数据库（用于初始化）
    
    该函数读取.env文件中的API配置，并将其存储到数据库中。
    只会处理以 _ENDPOINT 结尾的环境变量。
    对应的API密钥变量应命名为 {NAME}_API_KEY。
    
    注意：此操作会更新数据库中的现有配置或创建新配置。
    """
    load_dotenv()
    db = next(get_db())

    try:
        # 读取所有以 _ENDPOINT 结尾的环境变量
        for key in os.environ.keys():
            if key.endswith("_ENDPOINT"):
                # 从环境变量名称提取API配置名称
                name = key.replace("_ENDPOINT", "").lower()
                endpoint = os.environ[key]
                
                # 查找对应的API密钥环境变量
                api_key_var = f"{name.upper()}_API_KEY"
                api_key = os.environ.get(api_key_var)

                # 创建或更新配置
                config = db.query(ApiConfig).filter(ApiConfig.name == name).first()
                if not config:
                    # 创建新配置
                    config = ApiConfig(name=name, endpoint=endpoint)
                    db.add(config)
                else:
                    # 更新现有配置
                    config.endpoint = endpoint
                
                # 如果存在API密钥，则加密存储
                if api_key:
                    config.encrypted_key = secure_key_manager.encrypt_key(api_key)

                db.commit()
        print("✅ .env synced to DB")
    except SQLAlchemyError as e:
        db.rollback()
        print(f"❌ Database error syncing .env to DB: {e}")
    except Exception as e:
        db.rollback()
        print(f"❌ Error syncing .env to DB: {e}")
# config_sync.py
import os
from dotenv import load_dotenv, find_dotenv
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import ApiConfig
from database import get_db
from secure_keys import secure_key_manager

def sync_env_from_db():
    """从数据库同步配置到 .env 文件"""
    env_path = find_dotenv()
    if not env_path:
        raise FileNotFoundError(".env file not found")

    try:
        # 获取所有 API 配置
        db = next(get_db())
        configs = db.query(ApiConfig).all()

        # 构建新的 .env 内容
        lines = []
        for config in configs:
            key = config.name.upper().replace(" ", "_")
            endpoint_var = f"{key}_ENDPOINT"
            key_var = f"{key}_API_KEY"

            lines.append(f"{endpoint_var}={config.endpoint}")
            if config.encrypted_key:
                decrypted_key = secure_key_manager.decrypt_key(config.encrypted_key)
                lines.append(f"{key_var}={decrypted_key}")

        # 写入 .env 文件
        with open(env_path, 'w') as f:
            f.write('\n'.join(lines))
        print("✅ Config synced to .env")
    except Exception as e:
        print(f"❌ Error syncing config to .env: {e}")

def sync_db_from_env():
    """从 .env 文件同步配置到数据库（用于初始化）"""
    load_dotenv()
    db = next(get_db())

    try:
        # 读取所有以 _ENDPOINT 结尾的变量
        for key in os.environ.keys():
            if key.endswith("_ENDPOINT"):
                name = key.replace("_ENDPOINT", "").lower()
                endpoint = os.environ[key]
                api_key_var = f"{name.upper()}_API_KEY"
                api_key = os.environ.get(api_key_var)

                # 创建或更新配置
                config = db.query(ApiConfig).filter(ApiConfig.name == name).first()
                if not config:
                    config = ApiConfig(name=name, endpoint=endpoint)
                    db.add(config)
                else:
                    config.endpoint = endpoint
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
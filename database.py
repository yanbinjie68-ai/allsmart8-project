from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging
from sqlalchemy import text
# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SQLALCHEMY_DATABASE_URL = "sqlite:///./allsmart.db"

# 使用连接池
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,  # 每次使用前检查连接
    pool_recycle=3600,   # 3600秒后回收连接
     # 移除了SQLite不支持的pool_size和max_overflow参数
    # pool_size=10,        # 连接池大小
    # max_overflow=20      # 最大溢出连接数
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 在get_db函数中添加连接测试
def get_db():
    db = SessionLocal()
    try:
        # 测试数据库连接
        db.execute(text("SELECT 1"))
        yield db
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()
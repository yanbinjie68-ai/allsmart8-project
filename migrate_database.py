"""
数据库迁移脚本

该脚本负责初始化数据库表结构和添加缺失的列。
在项目首次运行或更新时执行此脚本以确保数据库结构是最新的。
"""
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from models import Base, ApiConfig
import os

def migrate_database():
    """
    执行数据库迁移
    
    该函数会创建所有缺失的表，并检查现有表中是否有缺失的列需要添加。
    适用于新安装和现有数据库的升级。
    """
    engine = create_engine("sqlite:///./allsmart.db", connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # 首先尝试创建所有表（适用于新安装）
    try:
        Base.metadata.create_all(bind=engine)
        print("数据库表创建完成")
    except Exception as e:
        print(f"创建表时出错: {e}")
    
    # 检查并添加缺失的列
    add_missing_columns(engine)
    
    print("数据库迁移完成")

def add_missing_columns(engine):
    """
    添加可能缺失的列
    
    当数据库结构更新但现有数据库缺少新列时，此函数会添加这些列。
    通过尝试查询列是否存在来检测缺失的列。
    
    Args:
        engine: SQLAlchemy数据库引擎
    """
    # 检查api_configs表是否缺少新添加的列
    try:
        # 尝试查询新添加的列来检查是否存在
        with engine.connect() as conn:
            # 检查music_genres列
            try:
                conn.execute("SELECT music_genres FROM api_configs LIMIT 1")
                print("music_genres列已存在")
            except OperationalError as e:
                if "no such column" in str(e):
                    # 添加music_genres列
                    conn.execute("ALTER TABLE api_configs ADD COLUMN music_genres TEXT")
                    print("已添加music_genres列")
            
            # 检查music_quality列
            try:
                conn.execute("SELECT music_quality FROM api_configs LIMIT 1")
                print("music_quality列已存在")
            except OperationalError as e:
                if "no such column" in str(e):
                    # 添加music_quality列
                    conn.execute("ALTER TABLE api_configs ADD COLUMN music_quality VARCHAR(20)")
                    print("已添加music_quality列")
            
            # 检查music_region列
            try:
                conn.execute("SELECT music_region FROM api_configs LIMIT 1")
                print("music_region列已存在")
            except OperationalError as e:
                if "no such column" in str(e):
                    # 添加music_region列
                    conn.execute("ALTER TABLE api_configs ADD COLUMN music_region VARCHAR(10)")
                    print("已添加music_region列")
            
            # 检查admins表的updated_at列
            try:
                conn.execute("SELECT updated_at FROM admins LIMIT 1")
                print("admins表的updated_at列已存在")
            except OperationalError as e:
                if "no such column" in str(e):
                    # 添加updated_at列
                    conn.execute("ALTER TABLE admins ADD COLUMN updated_at DATETIME")
                    print("已添加admins表的updated_at列")
                    
            # 检查users表的updated_at列
            try:
                conn.execute("SELECT updated_at FROM users LIMIT 1")
                print("users表的updated_at列已存在")
            except OperationalError as e:
                if "no such column" in str(e):
                    # 添加updated_at列
                    conn.execute("ALTER TABLE users ADD COLUMN updated_at DATETIME")
                    print("已添加users表的updated_at列")
                    
    except Exception as e:
        print(f"添加缺失列时出错: {e}")

if __name__ == "__main__":
    migrate_database()
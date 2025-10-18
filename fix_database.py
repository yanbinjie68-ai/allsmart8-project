import sqlite3
import os

# 连接到数据库
conn = sqlite3.connect('./allsmart.db')
cursor = conn.cursor()

# 检查admins表是否存在updated_at列
try:
    cursor.execute("SELECT updated_at FROM admins LIMIT 1")
    print("updated_at列已存在")
except sqlite3.OperationalError as e:
    if "no such column: updated_at" in str(e):
        # 添加缺失的列
        try:
            cursor.execute("ALTER TABLE admins ADD COLUMN updated_at DATETIME")
            print("成功添加updated_at列到admins表")
        except sqlite3.OperationalError as e2:
            print(f"添加列时出错: {e2}")
    else:
        print(f"检查列时出错: {e}")

# 检查users表是否存在updated_at列
try:
    cursor.execute("SELECT updated_at FROM users LIMIT 1")
    print("users表的updated_at列已存在")
except sqlite3.OperationalError as e:
    if "no such column: updated_at" in str(e):
        # 添加缺失的列
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN updated_at DATETIME")
            print("成功添加updated_at列到users表")
        except sqlite3.OperationalError as e2:
            print(f"添加列时出错: {e2}")
    else:
        print(f"检查列时出错: {e}")

# 提交更改并关闭连接
conn.commit()
conn.close()

print("数据库修复完成")
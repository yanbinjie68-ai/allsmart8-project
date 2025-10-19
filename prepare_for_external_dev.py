#!/usr/bin/env python3
"""
准备外发开发环境脚本

该脚本用于清理项目中的敏感信息，创建一个安全的外发开发版本。
"""

import os
import shutil
import re
from pathlib import Path

def clean_env_file():
    """清理.env文件中的敏感信息"""
    env_path = Path('.env')
    example_path = Path('.env.example')
    
    if env_path.exists():
        print("清理 .env 文件中的敏感信息...")
        # 读取.env文件内容
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换敏感信息为占位符
        # JWT密钥
        content = re.sub(r'SECRET_KEY=.*', 'SECRET_KEY=your-super-secret-jwt-key-here-change-in-production', content)
        
        # 加密密钥
        content = re.sub(r'ENCRYPTION_KEY=.*', 'ENCRYPTION_KEY=your-32-byte-base64-encoded-key-here==', content)
        
        # API密钥
        content = re.sub(r'API_KEY_ENCRYPTION_KEY=.*', 'API_KEY_ENCRYPTION_KEY=your-api-key-encryption-key-here', content)
        
        # 数据库URL
        content = re.sub(r'DATABASE_URL=.*', 'DATABASE_URL=sqlite:///./allsmart.db', content)
        
        # SMTP密码
        content = re.sub(r'SMTP_PASS=.*', 'SMTP_PASS=your-smtp-password-here', content)
        
        # 各种API密钥
        content = re.sub(r'OPENAI_API_KEY=.*', 'OPENAI_API_KEY=your-openai-api-key-here', content)
        content = re.sub(r'DEEPSEEK_API_KEY=.*', 'DEEPSEEK_API_KEY=your-deepseek-api-key-here', content)
        content = re.sub(r'SPOTIFY_CLIENT_SECRET=.*', 'SPOTIFY_CLIENT_SECRET=your-spotify-client-secret-here', content)
        content = re.sub(r'YOUTUBE_API_KEY=.*', 'YOUTUBE_API_KEY=your-youtube-api-key-here', content)
        content = re.sub(r'FACE_API_KEY=.*', 'FACE_API_KEY=your-face-api-key-here', content)
        content = re.sub(r'CHAT_SERVICE_TOKEN=.*', 'CHAT_SERVICE_TOKEN=your-chat-service-token-here', content)
        content = re.sub(r'IOT_BROKER_PASSWORD=.*', 'IOT_BROKER_PASSWORD=your-iot-broker-password-here', content)
        content = re.sub(r'FINGERPRINT_API_KEY=.*', 'FINGERPRINT_API_KEY=your-fingerprint-api-key-here', content)
        content = re.sub(r'VOICEPRINT_API_KEY=.*', 'VOICEPRINT_API_KEY=your-voiceprint-api-key-here', content)
        content = re.sub(r'IRIS_API_KEY=.*', 'IRIS_API_KEY=your-iris-api-key-here', content)
        content = re.sub(r'OCR_API_KEY=.*', 'OCR_API_KEY=your-ocr-api-key-here', content)
        content = re.sub(r'TTS_API_KEY=.*', 'TTS_API_KEY=your-tts-api-key-here', content)
        content = re.sub(r'STT_API_KEY=.*', 'STT_API_KEY=your-stt-api-key-here', content)
        
        # 保存清理后的内容
        with open('.env.cleaned', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("已创建清理后的 .env.cleaned 文件")

def create_external_dev_branch():
    """创建外发开发分支说明文件"""
    branch_readme = """
# 外发开发分支

此分支是为外部开发者准备的安全版本，已移除所有敏感信息。

## 安全措施

1. 所有API密钥、密码等敏感信息已替换为占位符
2. 数据库文件不包含真实数据
3. 环境变量文件仅包含示例配置

## 使用说明

1. 复制 `.env.example` 文件为 `.env`
2. 根据项目需求填写相应的配置项
3. 开发过程中请勿提交包含敏感信息的文件

## 重要提醒

- 请勿将任何包含真实密钥、密码的文件提交到版本控制系统
- 所有敏感信息应通过环境变量或安全的密钥管理系统提供
- 开发完成后，请确保代码审查时没有泄露敏感信息
    """
    
    with open('EXTERNAL_DEV_BRANCH.md', 'w', encoding='utf-8') as f:
        f.write(branch_readme)
    
    print("已创建外发开发分支说明文件")

def main():
    """主函数"""
    print("开始准备外发开发环境...")
    
    # 清理.env文件
    clean_env_file()
    
    # 创建外发开发分支说明
    create_external_dev_branch()
    
    print("\n外发开发环境准备完成！")
    print("\n请执行以下操作：")
    print("1. 检查并确认 .env.cleaned 文件中的敏感信息已被正确清理")
    print("2. 将项目推送到专门的外发开发仓库或分支")
    print("3. 提供给外部开发者时，说明安全开发规范")

if __name__ == "__main__":
    main()
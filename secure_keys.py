# secure_keys.py
"""
安全密钥管理模块

该模块负责API密钥的加密和解密操作，使用Fernet对称加密算法确保密钥安全存储。
在生产环境中，应使用强密钥并通过环境变量配置，避免硬编码在代码中。
"""
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import secrets

class SecureKeyManager:
    """
    安全密钥管理器类
    
    负责API密钥的加密和解密，使用环境变量中的加密密钥进行初始化，
    如果未设置则会生成一个临时密钥（仅用于开发环境）。
    """
    def __init__(self):
        """
        初始化安全密钥管理器
        从环境变量中读取加密密钥，如果不存在则生成一个临时密钥（仅用于开发环境）
        """
        # 从环境变量获取加密密钥
        env_key = os.getenv('ENCRYPTION_KEY')
        
        if not env_key or env_key == 'your-encryption-key-here' or env_key == '':
            # 如果没有设置环境变量或使用默认值，生成一个随机密钥
            # 注意：这仅适用于开发环境，生产环境必须使用固定的密钥
            self.key = Fernet.generate_key()
            print("Warning: Encryption key not set in environment variables. Using generated key.")
            print("For production, set ENCRYPTION_KEY in your .env file.")
        else:
            # 检查环境变量中的密钥是否是有效的Fernet密钥
            try:
                # 如果是有效的base64编码且长度正确，则直接使用
                decoded_key = base64.urlsafe_b64decode(env_key)
                if len(decoded_key) == 32:
                    self.key = env_key.encode() if isinstance(env_key, str) else env_key
                else:
                    # 如果长度不正确，生成新的有效密钥
                    self.key = Fernet.generate_key()
                    print("Warning: Invalid encryption key length in environment variables. Using generated key.")
                    print("Encryption key must be a 32-byte base64-encoded string.")
            except Exception:
                # 如果不是有效的base64编码，生成新的有效密钥
                self.key = Fernet.generate_key()
                print("Warning: Invalid encryption key format in environment variables. Using generated key.")
                print("Encryption key must be a valid base64-encoded 32-byte string.")
        
        # 确保最终的密钥是有效的Fernet密钥
        if isinstance(self.key, str):
            self.key = self.key.encode()
        
        # 创建Fernet实例
        self.cipher = Fernet(self.key)
    
    def encrypt_key(self, plain_text: str) -> str:
        """
        加密API密钥
        
        Args:
            plain_text (str): 明文API密钥
            
        Returns:
            str: 加密后的API密钥(base64编码)
            
        Raises:
            Exception: 加密过程中出现的任何错误
        """
        try:
            encrypted = self.cipher.encrypt(plain_text.encode())
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            raise Exception(f"Encryption failed: {str(e)}")
    
    def decrypt_key(self, encrypted_text: str) -> str:
        """
        解密API密钥
        
        Args:
            encrypted_text (str): 加密的API密钥(base64编码)
            
        Returns:
            str: 解密后的明文API密钥
            
        Raises:
            Exception: 解密过程中出现的任何错误
        """
        try:
            encrypted_bytes = base64.b64decode(encrypted_text)
            decrypted = self.cipher.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            raise Exception(f"Decryption failed: {str(e)}")

# 创建全局实例
secure_key_manager = SecureKeyManager()
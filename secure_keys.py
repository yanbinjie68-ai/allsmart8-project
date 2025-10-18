# secure_keys.py
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import secrets

class SecureKeyManager:
    def __init__(self):
        # 使用环境变量或生成密钥
        env_key = os.getenv('ENCRYPTION_KEY')
        
        if not env_key or env_key == 'your-encryption-key-here':
            # 如果没有设置环境变量或使用默认值，生成一个随机密钥
            self.key = Fernet.generate_key()
            print("Warning: Encryption key not set in environment variables. Using generated key.")
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
            except Exception:
                # 如果不是有效的base64编码，生成新的有效密钥
                self.key = Fernet.generate_key()
                print("Warning: Invalid encryption key format in environment variables. Using generated key.")
        
        # 确保最终的密钥是有效的Fernet密钥
        if isinstance(self.key, str):
            self.key = self.key.encode()
        
        # 创建Fernet实例
        self.cipher = Fernet(self.key)
    
    def encrypt_key(self, plain_text: str) -> str:
        """加密API密钥"""
        try:
            encrypted = self.cipher.encrypt(plain_text.encode())
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            raise Exception(f"Encryption failed: {str(e)}")
    
    def decrypt_key(self, encrypted_text: str) -> str:
        """解密API密钥"""
        try:
            encrypted_bytes = base64.b64decode(encrypted_text)
            decrypted = self.cipher.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            raise Exception(f"Decryption failed: {str(e)}")

# 创建全局实例
secure_key_manager = SecureKeyManager()
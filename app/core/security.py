"""Initialization or Placeholder File."""
# app/core/security.py
import hashlib
from cryptography.fernet import Fernet
from app.core.config import settings

fernet = Fernet(settings.FERNET_KEY.encode())

def hash_password(plain: str) -> str:
    return hashlib.sha256(plain.encode()).hexdigest()

def verify_password(plain: str, hashed: str) -> bool:
    return hashlib.sha256(plain.encode()).hexdigest() == hashed

def encrypt_bytes(plain_text: str) -> bytes:
    if plain_text is None:
        return None
    return fernet.encrypt(plain_text.encode())

def decrypt_bytes(cipher: bytes) -> str:
    if cipher is None:
        return None
    return fernet.decrypt(cipher).decode()

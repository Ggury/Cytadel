import secrets
import string
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated=  "auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def generate_activation_key (length = 32) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(secret=plain_password, hash=hashed_password)

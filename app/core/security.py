from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError,  InvalidHashError

ph = PasswordHasher()

def hash_password(password: str) -> str:
    return ph.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    try:
        return ph.verify(hashed, password)
    
    except (VerifyMismatchError, InvalidHashError):
        return False


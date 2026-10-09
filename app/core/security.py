from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError,  InvalidHashError

from datetime import datetime, timedelta, timezone
import jwt

from app.core.config import settings

ph = PasswordHasher()

def hash_password(password: str) -> str:
    return ph.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    try:
        return ph.verify(hashed, password)
    
    except (VerifyMismatchError, InvalidHashError):
        return False


def create_access_token(user_id: int | str) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_id),
        "exp": now + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        ),
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def decode_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        user_id = payload.get("sub")

        if not isinstance(user_id, str) or not user_id:
            return None

        return user_id

    except jwt.InvalidTokenError:
        return None

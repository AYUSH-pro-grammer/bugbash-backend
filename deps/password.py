from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _normalize_password(password: str) -> str:
    # bcrypt limit = 72 bytes
    # truncate safely BEFORE hashing
    return password.encode("utf-8")[:72].decode("utf-8", "ignore")


def hash_password(password: str) -> str:
    safe_password = _normalize_password(password)
    return pwd_context.hash(safe_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    safe_password = _normalize_password(plain_password)
    return pwd_context.verify(safe_password, hashed_password)

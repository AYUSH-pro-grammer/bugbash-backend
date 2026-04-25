from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from config.main import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


# 🔐 Swagger / OAuth2 integration


# -----------------------
# CREATE TOKEN
# -----------------------
def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# -----------------------
# DECODE TOKEN
# -----------------------
def decode_function(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


# -----------------------
# VERIFY TOKEN
# -----------------------
def verify_access_token(token: str) -> dict:
    payload = decode_function(token)

    if "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    return payload


# -----------------------
# GET CURRENT USER
# -----------------------
from fastapi import Depends

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:

    token = credentials.credentials  # extracts only the token

    payload = verify_access_token(token)
    return int(payload["sub"])
from pwdlib import PasswordHash
from datetime import timedelta, datetime, timezone
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from db import SessionDep
from sqlalchemy import select
from models import User
from typing import Annotated
from fastapi import Depends, HTTPException, status
from structs.auth_struct import TokenData
import os
import jwt

SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


def get_user(username: str, db: SessionDep) -> User | None:
    user = db.exec(select(User).filter(User.username == username)).first()
    if user:
        return user[0]
    return None


def get_password_hash(password):
    return password_hash.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: SessionDep):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("user")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(username=token_data.username, db=db)
    if user is None:
        raise credentials_exception
    return user

UserQuery = Annotated[User, Depends(get_current_user)]
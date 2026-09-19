from pwdlib import PasswordHash
from datetime import timedelta, datetime, timezone
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from db import SessionDep
from sqlalchemy import select
from models import User, Staff
from typing import Annotated
from fastapi import Depends, HTTPException, status
from structs.auth_struct import TokenData
import os
import jwt
# import hashlib
# import secrets

SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


# INVITE_EXPIRE_DAYS = 7


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


def user_from_token(token: str, db) -> User | None:
    "The user a JWT belongs to, or None if the token is invalid, expired or unknown"
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except InvalidTokenError:
        return None
    username = payload.get("user")
    if username is None:
        return None
    token_data = TokenData(username=username)
    return get_user(username=token_data.username, db=db)


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: SessionDep):
    user = user_from_token(token, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

UserQuery = Annotated[User, Depends(get_current_user)]


# Invite links: disabled while staff emails are placeholders (see api.py).
# def hash_invite_token(token: str) -> str:
#     "Invite tokens are only stored hashed, so a leaked database can't be used to claim accounts"
#     return hashlib.sha256(token.encode()).hexdigest()


# def new_invite_token() -> tuple[str, str, datetime]:
#     "Returns (token to hand to the staff member, hash to store, expiry)"
#     token = secrets.token_urlsafe(32)
#     expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(
#         days=INVITE_EXPIRE_DAYS
#     )
#     return token, hash_invite_token(token), expires_at


def create_staff_access_token(staff: Staff) -> str:
    """
    Staff tokens carry "staff" instead of "user", so user_from_token rejects them
    and a staff member can never reach the admin routes.
    """
    return create_access_token(
        {"staff": staff.id}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )


def staff_from_token(token: str, db) -> Staff | None:
    "The staff member a staff JWT belongs to, or None"
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except InvalidTokenError:
        return None
    staff_id = payload.get("staff")
    if not isinstance(staff_id, int):
        return None
    staff = db.get(Staff, staff_id)
    if staff is None or staff.deleted or staff.password is None:
        return None
    return staff


class PortalViewer:
    "Whoever is looking at the staff portal: a staff member, or an admin (creator)"

    def __init__(self, user: User | None = None, staff: Staff | None = None):
        self.user = user
        self.staff = staff


def get_portal_viewer(
    token: Annotated[str, Depends(oauth2_scheme)], db: SessionDep
) -> PortalViewer:
    staff = staff_from_token(token, db)
    if staff is not None:
        return PortalViewer(staff=staff)

    user = user_from_token(token, db)
    if user is not None:
        return PortalViewer(user=user)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


PortalQuery = Annotated[PortalViewer, Depends(get_portal_viewer)]

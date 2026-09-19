from pydantic import BaseModel
from typing import Literal

class AuthUser(BaseModel):
    id: int
    username: str
    role: Literal["admin", "staff"] = "admin"

class AuthResponse(BaseModel):
    token: str
    user: AuthUser
    
class Credentials(BaseModel):
    username: str
    password: str
    
class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    username: str | None = None



class PortalCredentials(BaseModel):
    "Staff sign in with their email. Admins sign in at /auth/login"
    email: str
    password: str


class EmailRequest(BaseModel):
    email: str


class PasswordRequest(BaseModel):
    "Create password / forgot password"
    email: str
    password: str


class AccountStatusResponse(BaseModel):
    has_account: bool


# Invite links: disabled while staff emails are placeholders (see api.py).
# class InviteSetup(BaseModel):
#     token: str
#     password: str
#
#
# class InviteResponse(BaseModel):
#     token: str
#     expires_at: str

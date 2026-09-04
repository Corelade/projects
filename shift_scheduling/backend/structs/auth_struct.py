from pydantic import BaseModel

class AuthUser(BaseModel):
    id: int
    username: str

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


from datetime import datetime
from pydantic import BaseModel


class UserModify(BaseModel):
    userEmail: str
    role: str


class UserGet(BaseModel):
    email: str


class UserResponse(BaseModel):
    username: str
    email: str
    registration_date: datetime
    account_status: str
    role: str
    is_verified: bool


class UserModifyResponse(BaseModel):
    userEmail: str
    role: str
    message: str


class UserBan(BaseModel):
    userEmail: str
    reason: str


class RoleLogs(BaseModel):
    role_email: str
    user_email: str
    reason: str


class ResetRequest(BaseModel):
    jwt: str

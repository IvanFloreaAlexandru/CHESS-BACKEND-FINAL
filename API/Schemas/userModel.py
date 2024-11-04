import datetime
import re
from typing import Optional

from pydantic import BaseModel, validator, EmailStr
from pydantic.v1 import Field


class UserCreate(BaseModel):
    username: str
    password: str
    email: str

    @validator('password')
    def password_is_strong(cls, value):
        """
        Parola trb sa contina :

        - minim 8 caractere
        - sa contina minim o litera mare
        - sa contina minim o litera mica
        - sa contina cel putin o cifra
        - sa contina cel putin un caracter special
        - sa nu contina ' sau "
        """

        min_length = 8
        if len(value) < min_length:
            raise ValueError(f"Password must be at least {min_length} characters long.")

        special_chars = r"[!@#$%^&*()\-+{}=|:<>?.\/\\`~]"

        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(char.islower() for char in value):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one digit.")
        if not any(char in special_chars for char in value):
            raise ValueError("Password must contain at least one special character.")

        if "'" in value or '"' in value:
            raise ValueError("Password cannot contain single or double quotes.")

        return value

    @validator('username')
    def username_good_format(cls, value):

        if not value.isalpha():
            raise ValueError("Username can contain only characters")
        if len(value) < 3:
            raise ValueError("Username should contain atleast 4 characters")
        if len(value) > 10:
            raise ValueError("Username should contain max 10 characters")
        return value


class UserModify(BaseModel):
    password: str

    @validator('password')
    def password_is_strong(cls, value):
        """
        Parola trb sa contina :

        - minim 8 caractere
        - sa contina minim o litera mare
        - sa contina minim o litera mica
        - sa contina cel putin o cifra
        - sa contina cel putin un caracter special
        - sa nu contina ' sau "
        """

        min_length = 8
        if len(value) < min_length:
            raise ValueError(f"Password must be at least {min_length} characters long.")

        special_chars = r"[!@#$%^&*()\-+{}=|:<>?.\/\\`~]"

        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(char.islower() for char in value):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one digit.")
        if not any(char in special_chars for char in value):
            raise ValueError("Password must contain at least one special character.")

        if "'" in value or '"' in value:
            raise ValueError("Password cannot contain single or double quotes.")

        return value


class UserGet(BaseModel):
    username: str
    email: str
    registration_date: datetime.datetime


class UserResponse(BaseModel):
    user_id: str
    username: str
    email: str
    password: str
    registration_date: datetime.datetime


class UserRecovery(BaseModel):
    email: str

    @validator('email')
    def validate_email_format(cls, value):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValueError("Invalid email format.")
        return value


class ResetPasswordRequest(BaseModel):
    new_password: str


class LoginResponse(BaseModel):
  access_token: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    totp_code: Optional[str] = None


class TokenResponse(BaseModel):
    token: str

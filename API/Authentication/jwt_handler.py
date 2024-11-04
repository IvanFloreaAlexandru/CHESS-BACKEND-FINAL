from datetime import timedelta
from typing import Optional

import jwt
from dotenv import dotenv_values
from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session
from starlette import status

from API.Schemas.jwtModels import JwtData
from API.security import manager
from storage.database import User
from storage.db_utils import get_db

env_vars = dotenv_values(".env")

JWT_SECRET = env_vars.get("JWT_SECRET")
JWT_ALGORITHM = env_vars.get("JWT_ALGORITHM")

jwt_router = APIRouter()


def sign_jwt(email: str, user_id: str):
    payload = {
        "email": email,
        "sub": user_id
    }

    token = manager.create_access_token(data=payload, expires=timedelta(days=7))
    return {
        "access_token": token
    }


def verify_jwt(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return {"message": "JWT Error: Token has expired"}
    except jwt.InvalidTokenError as e:

        return {"message": str(e)}


@manager.user_loader()
def callback_user_id(user_id):
    return user_id


def get_user_by_id(user_id: str, db: Session):
    user = db.query(User).filter(User.user_id == user_id).first()
    return user


@jwt_router.post("/verifyJwt")
def verify_jwt_endpoint(data: JwtData, db: Session = Depends(get_db), user_id: str = Depends(manager)):
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not logged in")
    payload = verify_jwt(data.jwt)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired JWT")

    user = get_user_by_id(payload["sub"], db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return {"detail": "JWT is valid", "user_id": user.user_id}


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session

from API.Authentication.jwt_handler import get_user_by_id
from API.Schemas.settingModels import User_Setting_Response
from API.security import manager
from storage.database import UserSetting
from storage.db_utils import get_db

user_settings_router = APIRouter(prefix="/user_settings", tags=["User Settings"])


'''@user_settings_router.post("/")
def create_user_setting(
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)) -> User_Setting_Response:

    user = get_user_by_id(user_id, db)

    userFound = db.query(User_Setting).filter(and_(User_Setting.userEmail == user.email)).first()

    if userFound:
        raise HTTPException(status_code=403, detail="USE1")

    db_user_setting = User_Setting(
        user_setting_id=str(uuid.uuid4()),
        userEmail=str(user.email),
        itemsPurchased="",
        settings=""
    )
    db.add(db_user_setting)
    db.commit()
    db.refresh(db_user_setting)

    return User_Setting_Response(
        user_setting_id=db_user_setting.user_setting_id,
        userEmail=db_user_setting.userEmail,
        itemsPurchased=db_user_setting.itemsPurchased,
        settings=db_user_setting.settings
    )'''


@user_settings_router.get("/get")
def get_user_setting(
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)
) -> User_Setting_Response:

    user = get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="")

    user_setting = db.query(UserSetting).filter(and_(UserSetting.userEmail == user.email)).first()

    if user_setting:
        return User_Setting_Response(
            user_setting_id=user_setting.user_setting_id,
            userEmail=user_setting.userEmail,
            itemsPurchased=user_setting.itemsPurchased,
            settings=user_setting.settings
        )
    else:
        raise HTTPException(status_code=400, detail="GUSE1")


@user_settings_router.put("/put")
def update_user_setting(
        data: User_Setting_Response,
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)
) -> User_Setting_Response:
    user = get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="")

    user_setting = db.query(UserSetting).filter(and_(UserSetting.userEmail == user.email)).first()
    if user_setting:
        user_setting.itemsPurchased = data.itemsPurchased
        user_setting.settings = data.settings
        db.commit()
        db.refresh(user_setting)
        return User_Setting_Response(
            itemsPurchased=user_setting.itemsPurchased,
            settings=user_setting.settings
        )
    else:
        raise HTTPException(status_code=404, detail="GUSE1")


'''@user_settings_router.delete("/delete")
def delete_user_setting(
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)):

    user = get_user_by_id(user_id, db)
    user_setting = db.query(User_Setting).filter(and_(User_Setting.userEmail == user.email)).first()

    if user_setting:
        db.delete(user_setting)
        db.commit()
        return {"message": "User settings deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="GUSE1")'''

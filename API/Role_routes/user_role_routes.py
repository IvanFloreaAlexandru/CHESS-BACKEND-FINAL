import datetime
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session
from API.Authentication.jwt_handler import get_user_by_id
from API.Role_models.userModel import UserModify, UserGet, UserResponse, UserModifyResponse, UserBan
from API.security import manager
from storage.db_utils import get_db
from storage.database import Roles, User, AdminLogs

user_role_router = APIRouter(tags=["Role Users"], prefix="/roles")

global_salt = "$2b$12$nrBd3QtspO23j7x.8.8Cuu"



@user_role_router.get("/get_user_info/", response_model=UserResponse)
def get_user_info(
        data: UserGet,
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)
) -> UserResponse:
    user = get_user_by_id(user_id, db)
    role_info = db.query(Roles).filter(and_(Roles.name == user.role)).first()

    if role_info and role_info.user_get:
        user_details = db.query(User).filter(User.email == data.email).first()
        if user_details:
            return UserResponse(
                username=user_details.username,
                email=user_details.email,
                registration_date=user_details.registration_date,
                account_status=user_details.account_status,
                role=user_details.role,
                is_verified=user_details.is_verified
            )
        else:
            raise HTTPException(status_code=404, detail="User not found")
    else:
        raise HTTPException(status_code=403, detail="User role doesn't allow this endpoint")


@user_role_router.put("/update_user_role", response_model=UserModifyResponse)
def update_user_info(
        data: UserModify,
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)
):
    user = get_user_by_id(user_id, db)
    role_info = db.query(Roles).filter(and_(Roles.name == user.role)).first()

    if role_info and role_info.user_update:
        user_details = db.query(User).filter(and_(User.email == data.userEmail)).first()
        if user_details:
            search_role = db.query(Roles).filter(and_(Roles.name == data.role)).first()
            if search_role:
                user_details.role = data.role
            else:
                raise HTTPException(status_code=404, detail="Role not found")
        else:
            raise HTTPException(status_code=404, detail="User not found")
    else:
        raise HTTPException(status_code=403, detail="User role doesn't allow this action")

    db.commit()
    db.refresh(user)

    return UserModifyResponse(
        userEmail=data.userEmail,
        role=data.role,
        message="Success!"
    )

# TODO restrictii de exemplu un grad de level 5 poate sa isi foloseasca comenzile pe unul de lvl 4, dar cel de level 4 nu poate sa le foloseasca pe unul de grad mai mare sau egal 4+


@user_role_router.put("/ban_user")
def ban_user(
        data: UserBan,
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)
):
    user = get_user_by_id(user_id, db)
    myRole = db.query(Roles).filter(and_(Roles.name == user.role)).first()
    if myRole:
        if not myRole.ban:
            raise HTTPException(status_code=404, detail="User role cant ban")
    else:
        raise HTTPException(status_code=404, detail="User role not found")

    banned_user_data = db.query(User).filter(User.email == data.userEmail).first()
    hisRole = db.query(Roles).filter(and_(banned_user_data.role == Roles.name)).first()
    if not banned_user_data:
        raise HTTPException(status_code=404, detail="User does not exist")
    else:
        if myRole.role_level <= hisRole.role_level:
            raise HTTPException(status_code=400,
                                detail="You cant do anything to a role that has the same role level as you")
        if not banned_user_data.account_status == "Banned":
            banned_user_data.account_status = "Banned"
            timenow = datetime.datetime.now()
            timeGoodFormat = timenow.strftime("%Y-%m-%d")
            logs = AdminLogs(role_email=user.email,
                             action="Ban",
                             log_id=str(uuid.uuid4()),
                             user_email=data.userEmail,
                             reason=data.reason,
                             date=timeGoodFormat)
            db.add(logs)
            db.commit()
        else:
            raise HTTPException(status_code=404, detail="User is already banned")
    return {"message": "User was banned"}

# TODO de pus restrictia cu role_levels pt fiecare endpoint (fara ban_user pt ca deja l-am facut)

# TODO save the role on role sanctions in other table named RoleOnRoleSanctions
@user_role_router.put("/unban_user")
def unban_user(
        data: UserBan,
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)
):
    user = get_user_by_id(user_id, db)
    user_role_data = db.query(Roles).filter(and_(Roles.name == user.role)).first()
    if user_role_data:
        if not user_role_data.unban:
            raise HTTPException(status_code=404, detail="D1")
    else:
        raise HTTPException(status_code=404, detail="User role not found")

    banned_user_data = db.query(User).filter(User.email == data.userEmail).first()
    if not banned_user_data:
        raise HTTPException(status_code=404, detail="User does not exist")
    else:
        if not banned_user_data.account_status == "Active":
            banned_user_data.account_status = "Active"
            timenow = datetime.datetime.now()
            timeGoodFormat = timenow.strftime("%Y-%m-%d")
            logs = AdminLogs(role_email=user.email,
                             action="Unban",
                             log_id=str(uuid.uuid4()),
                             user_email=data.userEmail,
                             reason=data.reason,
                             date=timeGoodFormat)
            db.add(logs)
            db.commit()
        else:
            raise HTTPException(status_code=404, detail="User is already unbanned")
    return {"message": "User was unbanned"}


@user_role_router.put("/warn_user")
def warn_user(
        data: UserBan,
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)
):
    user = get_user_by_id(user_id, db)
    user_role_data = db.query(Roles).filter(and_(Roles.name == user.role)).first()
    if user_role_data:
        if not user_role_data.ban:
            raise HTTPException(status_code=404, detail="D1")
    else:
        raise HTTPException(status_code=404, detail="User role not found")

    normal_user_data = db.query(User).filter(User.email == data.userEmail).first()
    if not normal_user_data:
        raise HTTPException(status_code=404, detail="User does not exist")
    else:
        if normal_user_data.account_status == "Active":
            normal_user_data.warningsNumber = normal_user_data.warningsNumber+1
            db.commit()
            timenow = datetime.datetime.now()
            timeGoodFormat = timenow.strftime("%Y-%m-%d")
            logs = AdminLogs(role_email=user.email,
                             action="Warn",
                             log_id=str(uuid.uuid4()),
                             user_email=data.userEmail,
                             reason=data.reason,
                             date=timeGoodFormat)
            db.add(logs)
            db.commit()
        else:
            raise HTTPException(status_code=404, detail="User is already unbanned")
    return {"message": "User was warned"}
# TODO la warn atunci cand face 3/3 ia automat ban pentru 1 saptamana, si se sterg warn-urile
# TODO istoric de sanctiuni pentru fiecare jucator


@user_role_router.put("/mute")
def mute_player(
        data: UserBan,
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)):

    user = get_user_by_id(user_id,db)
    myRole = db.query(Roles).filter(and_(Roles.name == user.role)).first()
    if myRole.mute:
        if data.userEmail:
            searched_user = db.query(User).filter(User.email == data.userEmail).first()
            if searched_user.cantTalk:
                raise HTTPException(status_code=400, detail="User is already muted")
            else:
                searched_user.cantTalk = True
                db.commit()
                timenow = datetime.datetime.now()
                timeGoodFormat = timenow.strftime("%Y-%m-%d")
                logs = AdminLogs(role_email=user.email,
                                 action="Mute",
                                 log_id=str(uuid.uuid4()),
                                 user_email=data.userEmail,
                                 reason=data.reason,
                                 date=timeGoodFormat)
                db.add(logs)
                db.commit()
                return {"message": "User was muted"}
        else:
            raise HTTPException(status_code=400,detail="User email should be filled")
    else:
        raise HTTPException(status_code=400, detail="You dont have access to mute")

# TODO perma and temporary ban,mute, warn expire, automatic temporary ban pentru 3/3 warn-uri


@user_role_router.put("/unmute")
def unmute_player(
        data: UserBan,
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)):

    user = get_user_by_id(user_id,db)
    user_role_data = db.query(Roles).filter(and_(Roles.name == user.role)).first()
    if user_role_data.unmute:
        if data.userEmail:
            searched_user = db.query(User).filter(User.email == data.userEmail).first()
            if not searched_user.cantTalk:
                raise HTTPException(status_code=400, detail="User is already unmuted")
            else:
                searched_user.cantTalk = False
                db.commit()
                timenow = datetime.datetime.now()
                timeGoodFormat = timenow.strftime("%Y-%m-%d")
                logs = AdminLogs(role_email=user.email,
                                 action="Unmute",
                                 log_id=str(uuid.uuid4()),
                                 user_email=data.userEmail,
                                 reason=data.reason,
                                 date=timeGoodFormat)
                db.add(logs)
                db.commit()
                return {"message": "User was unmuted"}
        else:
            raise HTTPException(status_code=400,detail="User email should be filled")
    else:
        raise HTTPException(status_code=400, detail="You dont have access to unmute")

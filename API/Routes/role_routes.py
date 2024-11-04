import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_
from sqlmodel import Session

from API.Authentication.jwt_handler import get_user_by_id
from API.Schemas.roleModels import RoleCreate, RoleDelete
from API.security import manager
from storage.database import Roles
from storage.db_utils import get_db

role_router = APIRouter(prefix="/roles", tags=["Roles"])


@role_router.post("/create")
def role_create(role_data: RoleCreate, db: Session = Depends(get_db)):
    # TODO de adaugat restrictie pt creare (doar cei ce au permisia role_create)
    role = Roles(
        role_id=str(uuid.uuid4()),
        name=role_data.name,
        role_create=role_data.role_create,
        role_delete=role_data.role_delete,
        role_level=role_data.role_level,
        ban=role_data.ban,
        unban=role_data.unban,
        mute=role_data.mute,
        unmute=role_data.unmute,
        warn=role_data.warn,
        user_get=role_data.user_get,
        user_update=role_data.user_update,
        user_delete=role_data.user_delete,
        user_settings_get=role_data.user_settings_get,
        user_settings_update=role_data.user_settings_update,
        user_statistics_get=role_data.user_statistics_get,
        user_statistics_update=role_data.user_statistics_update,
        friends_create=role_data.friends_create,
        friends_get=role_data.friends_get,
        friends_update=role_data.friends_update,
        friends_delete=role_data.friends_delete,
        games_create=role_data.games_create,
        games_get=role_data.games_get,
        games_update=role_data.games_update,
        games_delete=role_data.games_delete,
        moves_create=role_data.moves_create,
        moves_get=role_data.moves_get,
        moves_update=role_data.moves_update,
        moves_delete=role_data.moves_delete,
        profile_create=role_data.profile_create,
        profile_get=role_data.profile_get,
        profile_update=role_data.profile_update,
        profile_delete=role_data.profile_delete,
        tournament_registration_create=role_data.tournament_registration_create,
        tournament_registration_get=role_data.tournament_registration_get,
        tournament_registration_update=role_data.tournament_registration_update,
        tournament_registration_delete=role_data.tournament_registration_delete,
        tournament_create=role_data.tournament_create,
        tournament_get=role_data.tournament_get,
        tournament_update=role_data.tournament_update,
        tournament_delete=role_data.tournament_delete,)
    db.add(role)
    db.commit()
    db.refresh(role)
    return {"message": "Role created successfully"}

@role_router.delete("/delete_role")
def role_delete(role_data: RoleDelete, db: Session = Depends(get_db), user_id: str = Depends(manager)):
    user = get_user_by_id(user_id, db)
    user_permissions = db.query(Roles).filter(and_(Roles.name == user.role)).first()
    existing_role = db.query(Roles).filter(Roles.name == role_data.name).first()
    if existing_role:
        if user_permissions.role_delete:
            db.delete(existing_role)
            db.commit()
            return {"message": "You have succesfully deleted the role"}
        else:
            return {"message": "You dont have access to delete or create a role"}
    else:
        return {"message": "Role doesnt exist"}

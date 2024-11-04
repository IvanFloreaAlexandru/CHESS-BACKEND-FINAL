from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session

from API.Authentication.jwt_handler import get_user_by_id
from API.Schemas.moveModels import MoveResponse, GetMove
from API.security import manager
from storage.database import Move, Roles
from storage.db_utils import get_db

moves_role_router = APIRouter(prefix="/roles", tags=["Role-Moves"])


@moves_role_router.get("/get_move")
def get_move(
        data: GetMove,
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)):
    user = get_user_by_id(user_id,db)
    userPermission = db.query(Roles).filter(and_(Roles.name == user.role)).first()
    if userPermission.moves_get:
        move = db.query(Move).filter(Move.move_id == data.move_id).first()
        if not move:
            raise HTTPException(status_code=404, detail="MCE2")
        return MoveResponse(
            move_id=move.move_id,
            game_id=move.game_id,
            moves=move.moves
        )
    else:
        raise HTTPException(status_code=400, detail="User doesnt have that permission")

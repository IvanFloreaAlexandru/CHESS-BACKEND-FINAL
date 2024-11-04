from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from API.Authentication.jwt_handler import get_user_by_id
from API.Schemas.gameModels import GameResponse, GameUpdate
from API.Role_models.gameModels import UserGet
from API.security import manager
from storage.database import Game, Roles
from storage.db_utils import get_db

games_role_router = APIRouter(prefix="/roles", tags=["Role-Games"])


@games_role_router.get("/get_games", response_model=List[GameResponse])
def get_games(data: UserGet,
              db: Session = Depends(get_db),
              user_id: str = Depends(manager)
              ):
    user = get_user_by_id(user_id, db)
    userPermissions = db.query(Roles).filter(and_(Roles.name == user.role)).first()
    if userPermissions.games_get:
        games = db.query(Game).filter(
            or_(
                Game.player_1Email == data.userEmail,
                Game.player_2Email == data.userEmail
            )
        ).all()

        if games:
            return games
        else:
            raise HTTPException(status_code=404, detail="No games found for the user")
    else:
        raise HTTPException(status_code=400, detail="User doesnt have permission")


@games_role_router.put("/update_game")
def update_game(
        data: GameUpdate,
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)
):
    user = get_user_by_id(user_id, db)
    userPermissions = db.query(Roles).filter(and_(Roles.name == user.role)).first()
    if userPermissions.games_update:
        game = db.query(Game).filter(and_(Game.game_id == data.game_id)).first()
        if game:
            game.end_date_time = datetime.now()
            game.result = data.result
            db.commit()
            db.refresh(game)

            return GameResponse(
                game_id=game.game_id,
                player_1Email=game.player_1Email,
                player_2Email=game.player_2Email,
                start_date_time=game.start_date_time,
                end_date_time=game.end_date_time,
                result=game.result,
                white_pieces_playerEmail=game.white_pieces_playerEmail,
                black_pieces_playerEmail=game.black_pieces_playerEmail
            )
        else:
            raise HTTPException(status_code=404, detail="GCE2")
    else:
        raise HTTPException(status_code=400, detail="User doesnt have that permission")

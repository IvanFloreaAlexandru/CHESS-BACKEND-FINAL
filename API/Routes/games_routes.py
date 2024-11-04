import uuid
from datetime import datetime
from typing import List

import jwt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from API.Authentication.jwt_handler import get_user_by_id, JWT_SECRET, JWT_ALGORITHM
from API.Schemas.gameModels import GameCreate, GameResponse, GameDelete, GameUpdate
from API.security import manager
from storage.database import Game, UserStatistic
from storage.db_utils import get_db

games_router = APIRouter(prefix="/games", tags=["Games"])


# TODO verifica logica pentru game-uri

@games_router.post("/create")
def create_game(
        data: GameCreate,
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)
):
    user = get_user_by_id(user_id, db)

    white_player_payload = jwt.decode(data.white_player, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    black_player_payload = jwt.decode(data.black_player, JWT_SECRET, algorithms=[JWT_ALGORITHM])

    white_player_email = white_player_payload["email"]
    black_player_email = black_player_payload["email"]

    existing_game = db.query(Game).filter(
        and_(
            or_(
                Game.white_player == white_player_email,
                Game.black_player == white_player_email
            ),
            or_(
                Game.white_player == black_player_email,
                Game.black_player == black_player_email
            ),
            or_(
                Game.result_white == "Ongoing",
                Game.result_black == "Ongoing"
            )
        )
    ).first()

    if existing_game:
        return {"message": "Game already exists!"}  # aici e un raise HTTPException

    game_id = str(uuid.uuid4())

    db_game = Game(
        game_id=game_id,
        end_date_time=None,
        result_white="Ongoing",
        result_black="Ongoing",
        white_player=white_player_email,
        black_player=black_player_email
    )

    db.add(db_game)
    db.commit()
    db.refresh(db_game)

    return {"game_id": game_id, "status": "Game created successfully."}


@games_router.get("/", response_model=List[GameResponse])
def get_games(
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)
):
    user = get_user_by_id(user_id, db)

    games = db.query(Game).filter(
        or_(
            Game.white_player == user.email,
            Game.black_player == user.email
        )
    ).all()

    if games:
        return games
    else:
        raise HTTPException(status_code=404, detail="No games found for the user")


# Admin


@games_router.put("/put")
def update_game(
        data: GameUpdate,
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)
):
    user = get_user_by_id(user_id, db)
    game = db.query(Game).filter(
        and_(
            or_(Game.white_player == user.email, Game.black_player == user.email),
            or_(Game.result_white == "Ongoing", Game.result_black == "Ongoing"))
    ).first()

    if game:
        game.end_date_time = datetime.now()
        game.white_player = user.email
        game.result_white = data.result_white
        game.result_black = data.result_black
        db.commit()
        db.refresh(game)
        statistic = db.query(UserStatistic).filter(and_(user.email == UserStatistic.userEmail)).first()
        statistic.games_played = statistic.games_played + 1
        if game.result_white == "Won":
            statistic.wins = statistic.wins + 1
        elif game.result_white == "Lost":
            statistic.losses = statistic.losses + 1
        else:
            statistic.draws = statistic.draws
        statistic.winrate = (statistic.wins / statistic.games_played) * 100
        db.commit()
        db.refresh(statistic)
        statistic2 = db.query(UserStatistic).filter(and_(game.black_player == UserStatistic.userEmail)).first()
        statistic2.games_played = statistic.games_played + 1
        if game.result_black == "Won":
            statistic2.wins = statistic2.wins + 1
        elif game.result_black == "Lost":
            statistic2.losses = statistic2.losses + 1
        else:
            statistic2.draws = statistic2.draws
        db.commit()
        db.refresh(statistic2)
        return GameResponse(
            game_id=game.game_id,
            end_date_time=game.end_date_time,
            result_white=game.result_white,
            result_black=game.result_black,
            white_player=game.white_player,
            black_player=game.black_player
        )
    else:
        raise HTTPException(status_code=404, detail="GCE2")


# Admin
# Endpoint-ul asta ar trebui sa fie pentru grade, un user nu ar trebui sa poata sa isi stearga jocul din istoric

@games_router.delete("/delete")
def delete_game(
        data: GameDelete,
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)
):
    game = db.query(Game).filter(Game.game_id == data.game_id).first()
    user = get_user_by_id(user_id, db)
    if game:
        if game.player_1Email == user.email or game.player_2Email == user.email:
            db.delete(game)
            db.commit()
            return {"message": "Game deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Game not found")

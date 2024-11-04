import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session

from API.Authentication.jwt_handler import get_user_by_id
from API.Schemas.lookingModels import LookingForGamesCreate, LookingForGamesResponse, LookingForGamesUpdate
from API.security import manager
from storage.database import LookingForGames
from storage.db_utils import get_db

looking_router = APIRouter(prefix="/looking_for_games", tags=["Looking"])


@looking_router.post("/create")
def create_looking_for_game(
        data: LookingForGamesCreate,
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)):

    user = get_user_by_id(user_id, db)
    user_looking = db.query(LookingForGames).filter(and_(LookingForGames.userEmail == user.email)).first()
    if user_looking:
        raise HTTPException(status_code=404, detail="CLG1")
    db_looking_for_game = LookingForGames(
        userEmail=user.email,
        gamemode=data.gamemode,
        looking_id=str(uuid.uuid4())
    )

    db.add(db_looking_for_game)
    db.commit()
    db.refresh(db_looking_for_game)

    return LookingForGamesResponse(
        userEmail=db_looking_for_game.userEmail,
        gamemode=db_looking_for_game.gamemode,
        looking_id=db_looking_for_game.looking_id
    )


@looking_router.get("/get")
def get_looking_for_game(
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)
                         ):
    user = get_user_by_id(user_id, db)
    looking_for_game = db.query(LookingForGames).filter(and_(LookingForGames.userEmail == user.email)).first()
    if not looking_for_game:
        raise HTTPException(status_code=404, detail="CLG2")
    return LookingForGamesResponse(
        userEmail=looking_for_game.userEmail,
        gamemode=looking_for_game.gamemode,
        looking_id=looking_for_game.looking_id
    )


@looking_router.put("/put")
def update_looking_for_game(
        data: LookingForGamesUpdate,
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)
                            ):
    user = get_user_by_id(user_id, db)
    looking_for_game = db.query(LookingForGames).filter(and_(LookingForGames.userEmail == user.email)).first()
    if not looking_for_game:
        raise HTTPException(status_code=404, detail="CLG2")
    looking_for_game.userEmail = user.email
    looking_for_game.gamemode = data.gamemode
    db.commit()
    db.refresh(looking_for_game)
    return LookingForGamesResponse(
        userEmail=looking_for_game.userEmail,
        gamemode=looking_for_game.gamemode,
        looking_id=looking_for_game.looking_id
    )


@looking_router.delete("/delete")
def delete_looking_for_game(
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)
):
    user = get_user_by_id(user_id, db)
    looking_for_game = db.query(LookingForGames).filter(and_(LookingForGames.userEmail == user.email)).first()
    if not looking_for_game:
        raise HTTPException(status_code=404, detail="CLG2")
    db.delete(looking_for_game)
    db.commit()
    return {"message": "Looking for game deleted successfully"}

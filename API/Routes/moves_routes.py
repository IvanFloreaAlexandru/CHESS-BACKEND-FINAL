import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from API.Authentication.jwt_handler import get_user_by_id
from API.Schemas.moveModels import MoveCreate, MoveResponse, GetMove, MoveUpdate, DeleteMove
from API.security import manager
from storage.database import Move, Game
from storage.db_utils import get_db

moves_router = APIRouter(prefix="/moves", tags=["Moves"])


@moves_router.post("/create")
def create_move(
        data: MoveCreate,
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)):
    user = get_user_by_id(user_id, db)
    game_found = db.query(Game).filter(
        and_(
            or_(Game.white_player == user.email, Game.black_player == user.email),
            or_(Game.result_white == "Ongoing", Game.result_black == "Ongoing"))
    ).first()
    if game_found:
        repeated_game = db.query(Move).filter(and_(Move.game_id == game_found.game_id)).first()
    else:
        raise HTTPException(status_code=404, detail="Game not found")
    if repeated_game:
        raise HTTPException(status_code=400, detail="There is a game-match relationship created")
    db_move = Move(
        move_id=str(uuid.uuid4()),
        game_id=game_found.game_id,
        moves=data.moves
    )
    db.add(db_move)
    db.commit()
    db.refresh(db_move)
    return db_move


@moves_router.get("/get")
def get_move(
        data: GetMove,
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)):
    move = db.query(Move).filter(Move.move_id == data.move_id).first()
    if not move:
        raise HTTPException(status_code=404, detail="MCE2")
    return MoveResponse(
        move_id=move.move_id,
        game_id=move.game_id,
        moves=move.moves
    )


# Admin
@moves_router.put("/put")
def update_move(
        data: MoveUpdate,
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)
):
    user = get_user_by_id(user_id, db)
    game_found = db.query(Game).filter(
        and_(
            or_(Game.white_player == user.email, Game.black_player == user.email),
            or_(Game.result_white == "Ongoing", Game.result_black == "Ongoing"))
    ).first()
    if not game_found:
        raise HTTPException(status_code=400, detail="Game not found")
    move_found = db.query(Move).filter(and_(Move.game_id == game_found.game_id)).first()
    if not move_found:
        raise HTTPException(status_code=404, detail="MCE2")
    move_found.moves = data.moves
    db.commit()
    db.refresh(move_found)
    return MoveResponse(
        move_id=move_found.move_id,
        game_id=move_found.game_id,
        moves=move_found.moves
    )


# Admin


@moves_router.delete("/delete")
def delete_move(
        data: DeleteMove,
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)
):
    move = db.query(Move).filter(Move.move_id == data.move_id).first()
    if not move:
        raise HTTPException(status_code=404, detail="MCE2")
    db.delete(move)
    db.commit()
    return {"message": "Move deleted successfully"}

# de adaugat timp ca sa se poata prelua pentru a face ceasurile functionale, la fiecare move se pune data curenta
# pentru a face diferenta dintre datetime.datetime() si ultima mutare

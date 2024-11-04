from pydantic import BaseModel


class MoveCreate(BaseModel):
    moves: str


class MoveResponse(BaseModel):
    move_id: str
    game_id: str
    moves: str


class GetMove(BaseModel):
    move_id: str


class MoveUpdate(BaseModel):
    moves: str


class DeleteMove(BaseModel):
    move_id: str

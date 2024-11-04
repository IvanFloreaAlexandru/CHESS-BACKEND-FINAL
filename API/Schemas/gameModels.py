from typing import Optional

from pydantic import BaseModel
from datetime import datetime


class GameCreate(BaseModel):

    white_player: str
    black_player: str


class GameResponse(BaseModel):
    game_id: str
    end_date_time: Optional[datetime]
    white_player: Optional[str]
    black_player: Optional[str]
    result_white: str
    result_black: str


class GameUpdate(BaseModel):

    result_white: str
    result_black: str


class GameDelete(BaseModel):
    game_id: str

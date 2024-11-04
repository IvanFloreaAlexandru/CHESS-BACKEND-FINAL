from typing import Optional

from pydantic import BaseModel
from datetime import datetime


class GameResponse(BaseModel):
    player_1Email: str
    player_2Email: str
    start_date_time: datetime
    end_date_time: Optional[datetime]
    result: str
    white_pieces_playerEmail: Optional[str]
    black_pieces_playerEmail: Optional[str]


class UserGet(BaseModel):

    userEmail: str


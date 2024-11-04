from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TournamentCreate(BaseModel):
    name: str
    time_control: int
    type: str
    entry_fee: int
    prize_pool: int
    winnersEmail: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]


class TournamentResponse(BaseModel):
    tournament_id: str
    name: str
    start_date: datetime
    end_date: Optional[datetime]
    time_control: int
    type: str
    entry_fee: Optional[int]
    prize_pool: Optional[int]
    organizerEmail: str
    winnersEmail: Optional[str]


class TournamentUpdate(BaseModel):
    name: str
    end_date: str
    winnersEmail: str

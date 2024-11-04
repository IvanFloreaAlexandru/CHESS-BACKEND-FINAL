from datetime import datetime
from pydantic import BaseModel


class Tournament_Registration_Create(BaseModel):
    tournament_id: str


class Tournament_Registration_Response(BaseModel):
    registration_id: str
    tournament_id: str
    userEmail: str
    registration_date: datetime
    points_scored: int


class Tournament_Registration_Update(BaseModel):
    registration_id: str
    points_scored: int


class Tournament_Registration_Delete(BaseModel):
    registration_id: str

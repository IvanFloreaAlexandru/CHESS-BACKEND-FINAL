from pydantic import BaseModel


class User_Statistic_Response(BaseModel):
    games_played: int
    draws: int
    losses: int
    points: int


class UserGet(BaseModel):

    userEmail: str


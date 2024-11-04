from pydantic import BaseModel


class User_Statistic_Create(BaseModel):

    user_statistics_id: str
    userEmail: str
    games_played: int
    draws: int
    losses: int
    points: int


class User_Statistic_Response(BaseModel):

    games_played: int
    draws: int
    losses: int
    points: int
    wins: int

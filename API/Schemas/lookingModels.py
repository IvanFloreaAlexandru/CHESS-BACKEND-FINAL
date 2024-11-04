from pydantic import BaseModel


class LookingForGamesCreate(BaseModel):
    gamemode: str


class LookingForGamesUpdate(BaseModel):
    gamemode: str


class LookingForGamesResponse(BaseModel):
    userEmail: str
    gamemode: str
    looking_id: str

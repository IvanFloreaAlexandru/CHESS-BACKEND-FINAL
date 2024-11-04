from pydantic import BaseModel


class User_Setting_Create(BaseModel):

    userEmail: str


class User_Setting_Response(BaseModel):

    itemsPurchased: str
    settings: str

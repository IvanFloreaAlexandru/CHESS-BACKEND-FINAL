from pydantic import BaseModel


class FriendCreateOrDelete(BaseModel):
    friendEmail: str


class FriendUpdate(BaseModel):
    friendEmail: str
    status: str


class FriendResponse(BaseModel):

    friendship_id: str
    userEmail: str
    friendEmail: str
    status: str

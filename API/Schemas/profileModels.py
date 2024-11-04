from pydantic import BaseModel


class GetProfilesInfo(BaseModel):
    myJWT: str
    otherJWT: str


class NewDescription(BaseModel):

    newDescription: str

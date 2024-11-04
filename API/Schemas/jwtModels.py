from pydantic import BaseModel


class JwtData(BaseModel):

    jwt: str

from pydantic import BaseModel
from typing import Union

class Login(BaseModel):
    username: str
    password:str



class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Union[str, None] = None
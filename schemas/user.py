from typing import Optional
from datetime import date as date_type

from pydantic import BaseModel, EmailStr, constr, Field


class RegisterSchema(BaseModel):
    first_name: str = Field(min_length=3, max_length=15)
    last_name: str = Field(min_length=3, max_length=15)
    email:EmailStr
    password:str = Field(min_length=3, max_length=15)

class UserSchema(BaseModel):
    id:str
    first_name: Optional[str]
    last_name: Optional[str]
    email: EmailStr
    join_date: Optional[date_type]

    class Config():
        orm_mode = True

class UserPatch(BaseModel):
    first_name: Optional[str] = Field(min_length=3, max_length=15)
    last_name: Optional[str] = Field(min_length=3, max_length=15)
    email: Optional[EmailStr]
    password: Optional[str]

    class Config():
        orm_mode = True


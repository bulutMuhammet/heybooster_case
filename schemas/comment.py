from typing import Optional

from pydantic import BaseModel
from datetime import date as date_type

from schemas.project import ProjectSchema
from schemas.task import TaskSchema
from schemas.user import UserSchema


class CreateCommentSchema(BaseModel):
    content: str
    task_id : str

class PatchCommentSchema(BaseModel):
    content: str

class CommentSchema(BaseModel):
    id : str
    content: str
    created_date: date_type
    user: UserSchema
    task: TaskSchema

    class Config():
        orm_mode = True

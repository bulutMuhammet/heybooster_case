from typing import Optional
from pydantic.main import Enum
from pydantic import BaseModel
from schemas.project import ProjectSchema
from schemas.user import UserSchema
from datetime import datetime


class TaskSchema(BaseModel):
    id: int
    title: str
    content: str
    project: ProjectSchema
    creator: UserSchema
    assignee: Optional[UserSchema]
    status: str = None
    created_date: datetime


    class Config():
        orm_mode = True

class CreateTaskSchema(BaseModel):
    title: str
    content: str
    project_id: str



class AssignTaskSchema(BaseModel):
    assignee: int = None

class PatchTaskSchema(BaseModel):
    title: Optional[str]
    content: Optional[str]

class CreateTimeLogSchema(BaseModel):
    start_time: datetime
    end_time: datetime

class TimeLogSchema(BaseModel):
    start_time: datetime
    end_time: datetime
    task: TaskSchema

    class Config():
        orm_mode = True

class PatchTimeLogSchema(BaseModel):
    start_time: Optional[datetime]
    end_time: Optional[datetime]

class TaskStatus(str, Enum):
    assigned = 'assigned'
    started = 'started'
    in_review = 'in_review'
    done = 'done'

class SetStatusTaskSchema(BaseModel):
    status: TaskStatus
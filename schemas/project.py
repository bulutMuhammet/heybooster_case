from typing import Optional
from datetime import date as date_type
from pydantic import BaseModel
from pydantic.main import Enum
from schemas.user import UserSchema



class ProjectSchema(BaseModel):
    id:int
    name: str
    status: str
    created_date: Optional[date_type]
    user: UserSchema
    class Config():
        orm_mode = True

class Status(str, Enum):
    active = 'active'
    archived = 'archived'

class PermissionType(str, Enum):
    admin = 'admin'
    access = 'access'

class CreateProjectSchema(BaseModel):
    name: str
    status: Status = "active"

class PatchProjectSchema(BaseModel):
    name: Optional[str]
    status: Optional[Status]

class CreatePermissionSchema(BaseModel):
    project_id: str
    user_id: str
    permission_type: PermissionType

class PatchPermissionSchema(BaseModel):
    project_id: Optional[str]
    user_id: Optional[str]
    permission_type: Optional[PermissionType]
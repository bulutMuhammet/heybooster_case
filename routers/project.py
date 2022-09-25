from typing import List

from fastapi import APIRouter, Depends, status, HTTPException, Response, Query
from sqlalchemy.orm import Session

from helpers import check_permission
from models.user import User
from oauth2 import get_current_user
from schemas import user
from database import get_db
from models.project import Project, ProjectPermission
from schemas.project import ProjectSchema, CreateProjectSchema, PatchProjectSchema, \
    CreatePermissionSchema, PatchPermissionSchema

router = APIRouter(
    prefix="/projects",
    tags=['Projects']
)





@router.get("/", response_model=List[ProjectSchema])
def all(status: str = Query("", enum=["active", "archived"]),
        db: Session = Depends(get_db),
        current_user: user.UserSchema = Depends(get_current_user)):
    user = db.query(User).filter(User.email == current_user.email).first()
    permissions = [per.id for per in user.permissions]
    projects = db.query(Project).filter(Project.id.in_(permissions))
    if status:
        projects = projects.filter(Project.status == status)
    return projects.all()


@router.post("/", response_model=ProjectSchema)
def create(request: CreateProjectSchema, db: Session = Depends(get_db),
           current_user: user.UserSchema = Depends(get_current_user)):
    user = db.query(User).filter(User.email == current_user.email).first()
    req = request.dict()
    req["user_id"] = user.id
    project = Project(**req)

    db.add(project)
    db.commit()

    permission = ProjectPermission(user_id=user.id, project_id=project.id,
                                   permission_type="admin")
    db.add(permission)
    db.commit()

    return project


@router.patch("/{id}", response_model=ProjectSchema)
def patch_project(id: int, request: PatchProjectSchema, db: Session = Depends(get_db),
                  current_user: user.UserSchema = Depends(get_current_user)):
    check_permission("admin", current_user, id, db)
    project = db.query(Project).filter(Project.id == id)
    if not project.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"{id} Project Not found")
    project.update(request.dict(exclude_unset=True))
    db.commit()
    db.refresh(project.first())
    return project.first()


@router.get("/{id}", response_model=ProjectSchema)
def get(id: int,
        db: Session = Depends(get_db),
        current_user: user.UserSchema = Depends(get_current_user)):
    check_permission("admin", current_user, id, db)
    project = db.query(Project).filter(Project.id == id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"{id} Project Not found")
    return project


@router.post("/permissions")
def create_permission(request: CreatePermissionSchema, db: Session = Depends(get_db),
           current_user: user.UserSchema = Depends(get_current_user)):
    check_permission("admin", current_user, request.project_id, db)

    project = db.query(Project).filter(Project.id == request.project_id).first()
    user = db.query(User).filter(User.id == request.user_id).first()

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"{request.project_id} Project Not found")
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"{request.user_id} User Not found")

    permission = ProjectPermission(**request.dict())
    db.add(permission)
    db.commit()
    return permission

@router.patch("/permissions/{id}")
def patch_permission(id: int, request: PatchPermissionSchema, db: Session = Depends(get_db),
                  current_user: user.UserSchema = Depends(get_current_user)):
    permission = db.query(ProjectPermission).filter(ProjectPermission.id == id)
    check_permission("admin", current_user, permission.first().project_id, db)

    if not permission.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"{id} permission Not found")
    permission.update(request.dict(exclude_unset=True))
    db.commit()
    db.refresh(permission.first())
    return permission.first()

@router.delete("/permissions/{id}")
def delete_permission(id:int, db: Session = Depends(get_db),
           current_user: user.UserSchema = Depends(get_current_user)):
    permission = db.query(ProjectPermission).filter(ProjectPermission.id == id)

    if not permission.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"{id} Permission Not found")
    check_permission("admin", current_user, permission.first().project_id, db)

    permission.delete()
    db.commit()
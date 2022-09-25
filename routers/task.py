from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from celery_worker import notify
from database import get_db
from helpers import check_permission
from models.project import Project
from models.task import Task, TimeLog
from models.user import User
from oauth2 import get_current_user
from schemas import user
from schemas.task import CreateTaskSchema, TaskSchema, AssignTaskSchema, \
    PatchTaskSchema, CreateTimeLogSchema, TimeLogSchema, PatchTimeLogSchema, \
    SetStatusTaskSchema
from schemas.user import UserSchema

router = APIRouter(
    prefix="/tasks",
    tags=['Tasks']
)


def check_time_log_valid(start, end):
    if start > end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Start time must be greater than end time"
        )


@router.post("/", response_model=TaskSchema)
def create(request: CreateTaskSchema, db: Session = Depends(get_db),
           current_user: UserSchema = Depends(get_current_user)):
    check_permission("admin", current_user, request.project_id, db)
    user = db.query(User).filter(User.email == current_user.email).first()
    req = request.dict()
    req["creator_id"] = user.id
    project = Task(**req)
    db.add(project)
    db.commit()
    return project


@router.get("/", response_model=List[TaskSchema])
def all(project_id: int,
        db: Session = Depends(get_db),
        current_user: user.UserSchema = Depends(get_current_user)):
    check_permission("_all_", current_user, project_id, db)
    tasks = db.query(Task).filter(Task.project_id == project_id)
    if not db.query(Project).filter(Project.id == project_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"{project_id} Project Not found")
    return tasks.all()


@router.get("/{id}", response_model=TaskSchema)
def get(id: int,
        db: Session = Depends(get_db),
        current_user: user.UserSchema = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == id).first()
    check_permission("_all_", current_user, task.project_id, db)

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Task {id}  Not found")
    return task


@router.patch("/{id}", response_model=TaskSchema)
def patch_task(id: int, request: PatchTaskSchema, db: Session = Depends(get_db),
               current_user: user.UserSchema = Depends(get_current_user)):
    check_permission("admin", current_user, id, db)
    task = db.query(Task).filter(Task.id == id)
    if not task.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"{id} Task Not found")
    task.update(request.dict(exclude_unset=True))
    db.commit()
    db.refresh(task.first())
    return task.first()


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(id: int, db: Session = Depends(get_db),
                current_user: user.UserSchema = Depends(get_current_user)):
    check_permission("admin", current_user, id, db)
    task = db.query(Task).filter(Task.id == id)
    if not task.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"{id} Task Not found")
    task.delete()
    db.commit()


@router.post("/{id}/assigne", response_model=TaskSchema)
def assign_task(id: int, request: AssignTaskSchema, db: Session = Depends(get_db),
                current_user: user.UserSchema = Depends(get_current_user)):
    user_id = request.assignee
    if user_id != None:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"User {id}  Not found")
    task = db.query(Task).filter(Task.id == id)
    # this control is for creator

    if not task.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Task {id}  Not found")
    check_permission("admin", current_user, task.first().project_id,
                     db, raise_exception=True)
    #  if user_id != None that remove assignee of task
    if user_id == None:
        data = {"assignee_id": None, "assigne_date": func.now(), "status": None}
    else:
        # this control is for assignee
        permission = check_permission("_all_", user, task.first().project_id,
                                      db, raise_exception=False)
        if not permission:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"User {id} does not have permission to access this project")
        data = {"assignee_id": user.id, "assigne_date": func.now(),
                "status": "assigned"}
    task.update(data)
    db.commit()
    db.refresh(task.first())
    return task.first()


@router.get("/{task_id}/time_log", response_model=TimeLogSchema)
def get_time_log(task_id: int, db: Session = Depends(get_db),
                 current_user: user.UserSchema = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id)
    if not task.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Task {task_id}  Not found")
    check_permission("_all_", current_user, task.first().project_id, db)

    timelog = db.query(TimeLog).filter(TimeLog.task_id == task_id).first()
    if not timelog:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Time log not exists")

    return timelog


@router.post("/{task_id}/time_log", response_model=TimeLogSchema)
def create_time_log(task_id: int, request: CreateTimeLogSchema,
                    db: Session = Depends(get_db),
                    current_user: user.UserSchema = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id)
    if not task.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Task {task_id}  Not found")
    if current_user.email != task.first().assignee.email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You are not assignee of this task")

    timelog = db.query(TimeLog).filter(TimeLog.task_id == task_id).first()
    if timelog:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Time log already exists")

    req = request.dict()
    check_time_log_valid(req['start_time'], req['end_time'])

    req["task_id"] = task_id
    timelog = TimeLog(**req)
    db.add(timelog)
    db.commit()

    notify.apply_async(args=[timelog.id, task.first().project.user.email, "to_admin"],
                       eta=timelog.start_time)
    notify.apply_async(args=[timelog.id, task.first().project.user.email, "to_user"],
                       eta=timelog.end_time)
    # notify.apply(args=[timelog.id, task.first().project.user.email, "to_admin"])
    # notify.apply(args=[timelog.id, task.first().project.user.email, "to_user"])

    return timelog


@router.delete("/{task_id}/time_log")
def delete_time_log(task_id: int, db: Session = Depends(get_db),
                    current_user: user.UserSchema = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id)
    if not task.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"{task_id} Task Not found")
    if current_user.email != task.first().assignee.email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You are not assignee of this task")
    timelog = db.query(TimeLog).filter(TimeLog.task_id == task_id)
    if not timelog.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Time log not exists")
    timelog.delete()
    db.commit()


@router.post("/{task_id}/set_status", response_model=TaskSchema)
def set_status(task_id: int, request: SetStatusTaskSchema,
               db: Session = Depends(get_db),
               current_user: user.UserSchema = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id)
    if not task.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"{id} Task Not found")
    check_permission("_all_", current_user, task.first().project_id, db)

    task.update({"status": request.status})
    db.commit()
    db.refresh(task.first())
    return task.first()

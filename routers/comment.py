from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from helpers import check_permission
from models.comment import Comment
from models.task import Task
from models.user import User
from oauth2 import get_current_user
from schemas.comment import CommentSchema, CreateCommentSchema, PatchCommentSchema
from schemas.user import UserSchema

router = APIRouter(
    prefix="/comments",
    tags=['Comments']
)

def get_project_by_task(task_id, db):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Task {task_id}  Not found")
    return task.project_id

@router.get("/", response_model=List[CommentSchema])
def all(task_id: int,
        db: Session = Depends(get_db),
        current_user: UserSchema = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"{task_id} Task Not found")
    check_permission("_all_", current_user, task.project_id, db)
    comments = db.query(Comment).filter(Comment.task_id == task_id)
    return comments.all()

@router.post("/", response_model=CommentSchema)
def create(request: CreateCommentSchema, db: Session = Depends(get_db),
           current_user: UserSchema = Depends(get_current_user)):
    project = get_project_by_task(request.task_id, db)
    check_permission("admin", current_user, project,
                     db, raise_exception=True)
    user = db.query(User).filter(User.email == current_user.email).first()
    req = request.dict()
    req["user_id"] = user.id
    comment = Comment(**req)

    db.add(comment)
    db.commit()
    return comment

@router.patch("/{id}", response_model=CommentSchema)
def patch_comment(id:int,request: PatchCommentSchema, db: Session = Depends(get_db),
           current_user: UserSchema = Depends(get_current_user)):
    comment = db.query(Comment).filter(Comment.id == id)

    if not comment.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"{id} Comment Not found")
    if current_user.email != comment.first().user.email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You are not owner of this comment")
    comment.update(request.dict(exclude_unset=True))
    db.commit()
    db.refresh(comment.first())
    return comment.first()

@router.delete("/{id}")
def delete(id:int, db: Session = Depends(get_db),
           current_user: UserSchema = Depends(get_current_user)):
    comment = db.query(Comment).filter(Comment.id == id)

    if not comment.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"{id} Comment Not found")
    if current_user.email != comment.first().user.email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You are not owner of this comment")
    comment.delete()
    db.commit()

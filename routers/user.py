from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from hashing import Hash
from models.user import User
from oauth2 import get_current_user
from schemas import user as uschema

router = APIRouter(
    prefix="/user",
    tags=['user']
)


@router.post('/', response_model=uschema.UserSchema)
def create_user(request: uschema.RegisterSchema, db: Session = Depends(get_db)):
    req = request.dict()
    req["password"] = Hash.bcrypt(request.password)
    user = User(**req)
    db.add(user)
    db.commit()
    return user


@router.get('/me', response_model=uschema.UserSchema)
def me(db: Session = Depends(get_db),
       current_user: uschema.UserSchema = Depends(get_current_user)):
    user = db.query(User).filter(User.email == current_user.email).first()
    return user


@router.patch('/me', response_model=uschema.UserSchema)
def me(request: uschema.UserPatch, db: Session = Depends(get_db),
       current_user: uschema.UserSchema = Depends(get_current_user)):
    user = db.query(User).filter(User.email == current_user.email)
    user.update(request.dict(exclude_unset=True))
    db.commit()
    db.refresh(user.first())
    return user.first()


@router.get('/{id}', response_model=uschema.UserSchema)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"{id} User Not found")
    return user


@router.get('/', response_model=List[uschema.UserSchema])
def all(db: Session = Depends(get_db),
        current_user: uschema.UserSchema = Depends(get_current_user)):
    users = db.query(User).all()

    return users

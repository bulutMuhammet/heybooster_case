from fastapi import HTTPException, status

from models.project import ProjectPermission
from models.user import User


def check_permission(role, current_user, id, db, raise_exception=True):
    user = db.query(User).filter(User.email == current_user.email).first()
    permission = db.query(ProjectPermission).filter(
        ProjectPermission.user_id == user.id,
        ProjectPermission.project_id == id)
    if role != "_all_":
        permission=permission.filter(ProjectPermission.permission_type == role)
    if permission.first() is None:
        if raise_exception:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"You do not have {role} permission.")
        else:
            return False
    return True
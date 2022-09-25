from datetime import datetime
from sqlite3 import Date

from sqlalchemy import Column, Integer, String, DateTime, func, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    status = Column(String)
    created_date = Column(DateTime, default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="projects")
    permissions = relationship("ProjectPermission", back_populates="project")

class ProjectPermission(Base):
    __tablename__ = 'project_permissions'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User")
    project_id = Column(Integer, ForeignKey("projects.id"))
    project = relationship("Project")
    created_date = Column(DateTime, default=func.now())
    permission_type = Column(String, default="access")

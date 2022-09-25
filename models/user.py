from datetime import datetime

from sqlalchemy import Column, Integer, String, Date, DateTime, func, Boolean
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    password = Column(String)
    is_active = Column(Boolean)
    join_date = Column(DateTime, default=func.now())

    projects = relationship("Project")
    permissions = relationship("ProjectPermission")



from sqlalchemy import Column, Integer, String, DateTime, func, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(Text)
    status = Column(String)
    creator_id = Column(Integer, ForeignKey("users.id"))
    creator = relationship("User", foreign_keys='Task.creator_id')
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assignee = relationship("User", foreign_keys='Task.assignee_id')
    assigne_date = Column(DateTime, nullable=True)
    created_date = Column(DateTime, default=func.now())
    project_id = Column(Integer, ForeignKey("projects.id"))
    project = relationship("Project")

class TimeLog(Base):
    __tablename__ = 'timelogs'
    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    task = relationship("Task")
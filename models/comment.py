
from sqlalchemy import Column, Integer, String, DateTime, func, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User")
    task_id = Column(Integer, ForeignKey("tasks.id"))
    task = relationship("Task")
    created_date = Column(DateTime, default=func.now())

import datetime

from fastapi import FastAPI
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from pytz import timezone

from database import Base, engine, get_db
from models.project import Project
from models.user import User
from models.task import Task
from models.comment import Comment
from routers import project, auth, user, task, comment
from datetime import datetime, timedelta

app = FastAPI()

Base.metadata.create_all(engine)

app.include_router(project.router)
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(task.router)
app.include_router(comment.router)

#
# @app.post("/")
# def run_task():
#     my_tz = timezone('Europe/Istanbul')
#
#     # task = create_task.apply_async(eta=my_tz.localize(datetime.now()) + timedelta(seconds=20))
#
#     return JSONResponse({"Result": "d"})

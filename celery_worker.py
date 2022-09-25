import os
import yagmail
from sqlalchemy import create_engine
from celery import Celery
from dotenv import load_dotenv

load_dotenv(".env")

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND")

SQLALCHEMY_DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(SQLALCHEMY_DATABASE_URL)


@celery.task(name='send_email')
def send_email(subject: str, email_to: str, body: str):
    yag = yagmail.SMTP('*****', '********')
    yag.send(email_to, subject, body)


@celery.task(name="create_task")
def notify(time_log, email, notify_type):
    users = None
    con = engine.connect()
    time_log = con.execute(f'SELECT * FROM timelogs WHERE id = {time_log}').first()
    task_id = time_log[3]
    if not time_log:
        return
    task = con.execute(f'SELECT * FROM tasks  INNER JOIN users '
                       f'ON tasks.assignee_id=users.id where tasks.id = {task_id}').first()
    task_status = task[3]
    user = task[12]
    con.close()
    # that means user did not finished task end time
    if notify_type == "to_admin":
        if task_status != "done":
            message = f"User ({user}) Didn't finish the task({task_id}) on the promised end time\n"
            send_email("Notification", email, message)

    # that means user did not started task start time
    if notify_type == "to_user":
        if task_status != "done":
            message = f"You didn't start the task({task_id}) on the promised start time\n"
            send_email("Notification", email, message)

# heybooster jira clone case app

In this application, you can create projects, assign tasks to projects, and manage tasks.

# Installation manually

### Install virtual env

`pip install virtualenv
`
<br> <br>
`virtualenv venv 
`


### Deactivate virtual env:

`deactivate
`

### Activate virtual env:

`
.\venv\Scripts\activate
`
### Install requirements:

`pip install -r requirements.txt

### Run redis (firstly you need to install redis)
`celery -A celery_worker.celery worker --loglevel=info -P eventlet`

### And run server
`uvicorn main:app --reload` 

# Installation with docker

### Build docker 

'docker-compose build'

### Run docker 

'docker-compose run'


## Enter credentials of mail config to celery_worker.py

`yag = yagmail.SMTP('*****', '********')`


# Used Technogies
- FastAPI 
- Celery
- SQLAlchemy
- PostgreSQL
- Docker
- Redis
- Yagmail

# See API documentation
`127.0.0.1:8000/docs`
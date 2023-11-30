FROM python:3.11.6-slim

RUN pip install -U pip
RUN pip install pipenv 

WORKDIR /app

COPY [ "Pipfile", "Pipfile.lock", "./" ]

RUN pipenv install --system --deploy

COPY [".env", "main.py", "./"]

# EXPOSE 9696

# ENTRYPOINT [ "gunicorn", "--bind=0.0.0.0:9696", "main:app" ]

# kalo mau run gunicorn-nya di dalam folder pake `gunicorn --bind=0.0.0.0:9696 --chdir web-service-mlflow main:app`

FROM python:3.11-slim

RUN mkdir /app
WORKDIR /app

COPY . /app

RUN pip install -U pipenv

RUN pipenv install --deploy --ignore-pipfile

EXPOSE 8080

CMD ["pipenv", "run", "gunicorn", "-b", "0.0.0.0:8080", "index:app"]

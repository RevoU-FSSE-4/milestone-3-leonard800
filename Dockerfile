FROM python:3.11-slim

WORKDIR /

COPY Pipfile Pipfile.lock ./

RUN pip install pipenv

RUN pipenv install --deploy --ignore-pipfile

COPY . .

EXPOSE 5000

ENV FLASK_APP=index.py
ENV FLASK_ENV=production

CMD ["pipenv", "run", "flask", "run", "--host=0.0.0.0"]

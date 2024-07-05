FROM python:3.11-slim

WORKDIR /

COPY Pipfile Pipfile.lock ./

RUN pip install pipenv
RUN pipenv install --deploy --ignore-pipfile

COPY . .

EXPOSE 8080

CMD ["pipenv", "run", "flask", "run", "--host=0.0.0.0"]

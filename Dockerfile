FROM python:3.10

WORKDIR /app

RUN pip install pipenv
COPY Pipfile.lock /app
COPY Pipfile /app
RUN pipenv install --system --deploy --ignore-pipfile

COPY src/ /app/
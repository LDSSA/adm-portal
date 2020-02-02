FROM python:3.7-alpine3.10

ENV PIP_DISABLE_PIP_VERSION_CHECK=on

RUN pip install poetry==0.12.17

WORKDIR /app
COPY poetry.lock pyproject.toml /app/

RUN poetry config settings.virtualenvs.create false
RUN poetry install --no-dev --no-interaction --no-ansi

COPY . /app

EXPOSE 8000

CMD ./serve.sh

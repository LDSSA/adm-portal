FROM python:3.8-buster

ENV PIP_DISABLE_PIP_VERSION_CHECK=on

RUN pip install poetry==1.0.5

RUN poetry --version

RUN groupadd -r adm-portal; \
    useradd -u 1000 -r -M -d /app -g adm-portal -s /bin/false adm-portal;

WORKDIR /app
COPY poetry.lock pyproject.toml /app/

RUN poetry config virtualenvs.create false
RUN poetry install --no-dev --no-interaction --no-ansi

COPY . /app

EXPOSE 8000
USER adm-portal

CMD ./serve.sh

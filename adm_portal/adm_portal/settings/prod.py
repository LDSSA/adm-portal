import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *  # noqa: F401 F403 F405

ENV = "prod"


# Django Settings
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]  # noqa: F405

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ["POSTGRES_NAME"],  # noqa: F405
        "USER": os.environ["POSTGRES_USER"],  # noqa: F405
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],  # noqa: F405
        "HOST": os.environ["POSTGRES_HOST"],  # noqa: F405
        "PORT": os.environ["POSTGRES_PORT"],  # noqa: F405
    }
}

# Custom Settings
EMAIL_CLIENT = "ELASTIC"
ELASTIC_EMAIL_API_KEY = os.environ["ELASTIC_EMAIL_API_KEY"]  # noqa: F405
ELASTIC_EMAIL_SENDER = os.environ["ELASTIC_EMAIL_SENDER"]  # noqa: F405

STORAGE_CLIENT = "S3"
STORAGE_BUCKET = os.environ["S3_BUCKET_NAME"]  # noqa: F405

FF_CLIENT = "DB"

GRADER_CLIENT = "HTTP"
GRADER_CLIENT_URL = os.environ["ADM_GRADER_URL"]  # noqa: F405
GRADER_CLIENT_AUTH_TOKEN = os.environ["ADM_GRADER_AUTH_TOKEN"]  # noqa: F405


# Custom Integrations
sentry_sdk.init(dsn=os.environ["SENTRY_URL"], integrations=[DjangoIntegration()], send_default_pii=True)  # noqa: F405

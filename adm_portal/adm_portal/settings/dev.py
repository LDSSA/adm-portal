import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *  # noqa: F401 F403

ENV = "dev"


# Django Settings
SECRET_KEY = "SECRET"

DEBUG = True

DATABASES = {
    "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": os.path.join(BASE_DIR, "dev-db.sqlite3")}  # noqa: F405
}


# Custom Settings
EMAIL_CLIENT = "LOCAL"
EMAIL_LOCAL_DIR = os.path.join(os.path.dirname(BASE_DIR), ".mailbox")  # noqa: F405

STORAGE_CLIENT = "S3"
STORAGE_BUCKET = "ldssa-adm-portal-601"

FF_CLIENT = "DB"

GRADER_CLIENT = "HTTP"
GRADER_CLIENT_URL = os.environ.get("ADM_GRADER_URL", "http://0.0.0.0:3000")  # noqa: F405
GRADER_CLIENT_AUTH_TOKEN = os.environ.get("ADM_GRADER_AUTH_TOKEN", "dev-secret")  # noqa: F405


# Custom Integrations
SENTRY_URL = os.environ.get("SENTRY_URL", None)  # noqa: F405
if SENTRY_URL is not None:
    sentry_sdk.init(dsn=SENTRY_URL, integrations=[DjangoIntegration()], send_default_pii=True)

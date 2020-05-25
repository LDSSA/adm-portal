from .base import *  # noqa: F401 F403

ENV = "ci"


# Django Settings
SECRET_KEY = "CI-SECRET"

DEBUG = False

DATABASES = {
    "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": os.path.join(BASE_DIR, "ci-db.sqlite3")}  # noqa: F405
}


# Custom Settings
EMAIL_CLIENT = "LOCAL"
EMAIL_LOCAL_DIR = os.path.join(os.path.dirname(BASE_DIR), ".ci-mailbox")  # noqa: F405

STORAGE_CLIENT = "LOCAL"
STORAGE_LOCAL_DIR = os.path.join(os.path.dirname(BASE_DIR), ".ci-storage")  # noqa: F405

FF_CLIENT = "MOCK"

GRADER_CLIENT = "FAKE"

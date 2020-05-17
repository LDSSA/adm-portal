from .base import *  # noqa: F403 F401

ENV = "dev"

SECRET_KEY = "SECRET"

DEBUG = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {"django": {"handlers": ["console"], "level": "INFO", "propagate": False}},
}

EMAIL_CLIENT = "LOCAL"
LOCAL_EMAIL_CLIENT_ROOT = os.path.join(os.path.dirname(BASE_DIR), ".mailbox")  # noqa: F405

STORAGE_CLIENT = "S3"
STORAGE_CLIENT_NAMESPACE = "ldssa-adm-portal-601"

FF_CLIENT = "DB"

GRADER_CLIENT = "HTTP"
GRADER_CLIENT_URL = os.environ.get("ADM_GRADER_URL", "http://0.0.0.0:3000")  # noqa: F405
GRADER_CLIENT_AUTH_TOKEN = os.environ.get("ADM_GRADER_AUTH_TOKEN", "dev-secret")  # noqa: F405

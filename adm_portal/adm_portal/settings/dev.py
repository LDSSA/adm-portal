from .base import *  # noqa: F403 F401

SECRET_KEY = "secret"

DEBUG = True

EMAIL_CLIENT = "LOCAL"
LOCAL_EMAIL_CLIENT_ROOT = os.path.join(os.path.dirname(BASE_DIR), ".mailbox")  # noqa: F405

STORAGE_CLIENT = "LOCAL"
STORAGE_CLIENT_NAMESPACE = os.path.join(os.path.dirname(BASE_DIR), ".storage")  # noqa: F405

FF_CLIENT = "DB"

GRADER_CLIENT = "FAKE"

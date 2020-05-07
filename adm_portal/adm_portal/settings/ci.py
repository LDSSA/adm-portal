from .base import *  # noqa: F403 F401

SECRET_KEY = "CI-SECRET"

DEBUG = False

EMAIL_CLIENT = "LOCAL"
LOCAL_EMAIL_CLIENT_ROOT = os.path.join(os.path.dirname(BASE_DIR), ".ci-mailbox")  # noqa: F405

STORAGE_CLIENT = "LOCAL"
STORAGE_CLIENT_NAMESPACE = os.path.join(os.path.dirname(BASE_DIR), ".ci-storage")  # noqa: F405

FF_CLIENT = "MOCK"

GRADER_CLIENT = "FAKE"

from .base import *  # noqa: F403 F401

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]  # noqa: F405

DEBUG = False


EMAIL_CLIENT = "ELASTIC"
ELASTIC_EMAIL_API_KEY = os.environ["ELASTIC_EMAIL_API_KEY"]  # noqa: F405
ELASTIC_EMAIL_SENDER = "mariacristinavfdominguez@gmail.com"

STORAGE_CLIENT = "S3"
STORAGE_CLIENT_NAMESPACE = "ldssa-adm-portal-601"

FF_CLIENT = "DB"

GRADER_CLIENT = "HTTP"
GRADER_CLIENT_URL = os.environ["ADM_GRADER_URL"]  # noqa: F405
GRADER_CLIENT_AUTH_TOKEN = os.environ["ADM_GRADER_AUTH_TOKEN"]  # noqa: F405

import os
import typing

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS: typing.List[str] = ["*"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    #
    "users",
    "staff",
    "profiles",
    "email_client",
    "applications",
    "payments",
    "commands",
    "selected",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "adm_portal.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates", "users", "profiles", "candidate", "staff"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

WSGI_APPLICATION = "adm_portal.wsgi.application"

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": os.path.join(BASE_DIR, "db.sqlite3")}}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = False

USE_L10N = False

USE_TZ = False

STATIC_URL = "/static/"

AUTHENTICATION_BACKENDS = ["users.backends.EmailModelBackend"]

AUTH_USER_MODEL = "users.User"

# Custom settings
# todo: move these settings to dev/prod and set them up properly

# one of: "LOCAL"
# EMAIL_CLIENT = "LOCAL"
# LOCAL_EMAIL_CLIENT_ROOT is required for
# LOCAL_EMAIL_CLIENT_ROOT = os.path.join(os.path.dirname(BASE_DIR), ".mailbox")

# ELASTICEMAIL_API_URL = "https://api.elasticemail.com/v2/email/send"
# ELASTICEMAIL_API_FROM = "mariacristinavfdominguez@gmail.com"

# one of: "S3", "LOCAL"
# STORAGE_CLIENT = "S3"
# STORAGE_CLIENT_NAMESPACE = "ldssa-adm-portal"

# one of: "DB", "MOCK"
# FF_CLIENT = "DB"

# one of: "HTTP", "FAKE"
# GRADER_CLIENT = "FAKE"
# GRADER_CLIENT_URL is required when GRADER_CLIENT = "HTTP"
# GRADER_CLIENT_URL = "https://mflpriku65.execute-api.eu-west-1.amazonaws.com/Prod/"
# required when GRADER_CLIENT = "HTTP"
# GRADER_CLIENT_AUTH_TOKEN = os.environ.get("AUTH_TOKEN")

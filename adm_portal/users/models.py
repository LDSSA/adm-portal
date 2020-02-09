import uuid
from typing import NamedTuple

from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models

from .managers import UserManager


def get_default_uuid():
    return uuid.uuid4().hex


class User(AbstractBaseUser):
    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    uuid = models.CharField(
        max_length=32, editable=False, null=False, blank=False, unique=True, default=get_default_uuid
    )

    email = models.EmailField(blank=False, null=False, unique=True)

    is_staff = models.BooleanField(default=False, null=False)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class UserData(NamedTuple):
    id: str
    uuid: str
    email: str
    is_staff: bool


def to_user_data(u: User) -> UserData:
    return UserData(id=u.id, uuid=u.uuid, email=u.email, is_staff=u.is_staff)

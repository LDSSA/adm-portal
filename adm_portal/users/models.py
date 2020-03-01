import uuid
from typing import Any

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, **kwargs: Any):
        email_ = kwargs["email"]
        password = kwargs["password"]
        is_staff = kwargs.get("is_staff", False)
        email_confirmed = kwargs.get("email_confirmed", False)
        code_of_conduct_accepted = kwargs.get("code_of_conduct_accepted", False)
        email = self.normalize_email(email_)
        user = self.model(
            email=email,
            is_staff=is_staff,
            email_confirmed=email_confirmed,
            code_of_conduct_accepted=code_of_conduct_accepted,
        )
        user.set_password(password)
        user.save(using=self._db)
        if not user.email_confirmed:
            UserConfirmEmail.objects.create(user=user)
        return user

    def create_staff_user(self, **kwargs: str):
        return self.create_user(is_staff=True, email_confirmed=True, code_of_conduct_accepted=True, **kwargs)


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
    email_confirmed = models.BooleanField(default=False, null=False)
    code_of_conduct_accepted = models.BooleanField(default=False, null=False)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class UserToken(models.Model):
    user = models.OneToOneField("users.User", on_delete=models.CASCADE)

    token = models.CharField(max_length=32, editable=False, null=False, unique=True, default=get_default_uuid)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class UserConfirmEmail(UserToken):
    pass


class UserResetPassword(UserToken):
    pass

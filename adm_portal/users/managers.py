from typing import Any

from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, **kwargs: Any):
        email_ = kwargs["email"]
        password = kwargs["password"]
        is_staff = kwargs.get("is_staff", False)
        email = self.normalize_email(email_)
        user = self.model(email=email, is_staff=is_staff)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staff_user(self, **kwargs: str):
        return self.create_user(is_staff=True, **kwargs)

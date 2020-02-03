from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, **kwargs):
        email_ = kwargs["email"]
        password = kwargs["password"]
        email = self.normalize_email(email_)
        user = self.model(email=email)
        user.set_password(password)
        user.save(using=self._db)
        return user

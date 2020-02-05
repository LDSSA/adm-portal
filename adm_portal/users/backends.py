from typing import Any

from django.contrib.auth import get_user_model
from django.http import HttpRequest

User = get_user_model()


class EmailModelBackend:
    def authenticate(self, request: HttpRequest, email: str = None, password: str = None) -> Any:
        user = None

        if email is not None:
            try:
                user_ = User.objects.get(email=email)
                if user_.check_password(password):
                    user = user_
            except User.DoesNotExist:
                # waste time on purpose
                User().set_password(password)  # type: ignore

        return user

    def get_user(self, user_id: int) -> Any:
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

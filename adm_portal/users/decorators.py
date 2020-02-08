from typing import Any, Callable

from django.contrib.auth.decorators import user_passes_test


def requires_candidate_login(f: Callable[[Any], Any]) -> Callable[[Any], Any]:
    return user_passes_test(lambda u: u.is_authenticated and not u.is_staff, login_url="/account/login")(f)


def requires_staff_login(f: Callable[[Any], Any]) -> Callable[[Any], Any]:
    return user_passes_test(lambda u: u.is_authenticated and u.is_staff, login_url="/account/login")(f)

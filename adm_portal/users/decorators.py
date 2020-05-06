from typing import Any, Callable

from django.contrib.auth.decorators import user_passes_test


def u_is_authenticated(u: Any) -> bool:
    return u.is_authenticated


def u_confirmed_email(u: Any) -> bool:
    return u_is_authenticated(u) and getattr(u, "email_confirmed", False)


def u_accepted_coc(u: Any) -> bool:
    return u_confirmed_email(u) and getattr(u, "code_of_conduct_accepted", False)


def requires_candidate_login(f: Callable[..., Any]) -> Callable[..., Any]:
    return user_passes_test(
        lambda u: u_is_authenticated(u) and not u.is_staff, redirect_field_name=None, login_url="/account/login"
    )(f)


def requires_candidate_confirmed(f: Callable[..., Any]) -> Callable[..., Any]:
    return user_passes_test(
        lambda u: u_confirmed_email(u) and not u.is_staff, redirect_field_name=None, login_url="/candidate/home"
    )(f)


def requires_candidate_coc(f: Callable[..., Any]) -> Callable[..., Any]:
    return user_passes_test(
        lambda u: u_accepted_coc(u) and not u.is_staff, redirect_field_name=None, login_url="/candidate/home"
    )(f)


def requires_staff_login(f: Callable[..., Any]) -> Callable[..., Any]:
    return user_passes_test(
        lambda u: u_is_authenticated(u) and u.is_staff, redirect_field_name=None, login_url="/account/login"
    )(f)

from typing import Any, Callable

from django.contrib.auth.decorators import user_passes_test


def is_staff_or_admin(u: Any) -> bool:
    return u.is_staff or u.is_admin


def u_is_authenticated(u: Any) -> bool:
    return u.is_authenticated


def u_confirmed_email(u: Any) -> bool:
    return u_is_authenticated(u) and getattr(u, "email_confirmed", False)


def u_accepted_coc(u: Any) -> bool:
    return u_confirmed_email(u) and getattr(u, "code_of_conduct_accepted", False)


def u_decided_scholarship(u: Any) -> bool:
    return u_accepted_coc(u) and getattr(u, "applying_for_scholarship", None) is not None


def u_has_profile(u: Any) -> bool:
    return u_decided_scholarship(u) and getattr(u, "profile", None) is not None


def requires_candidate_login(f: Callable[..., Any]) -> Callable[..., Any]:
    return user_passes_test(
        lambda u: u_is_authenticated(u) and not is_staff_or_admin(u),
        redirect_field_name=None,
        login_url="/account/login",
    )(f)


def requires_candidate_confirmed(f: Callable[..., Any]) -> Callable[..., Any]:
    return user_passes_test(
        lambda u: u_confirmed_email(u) and not is_staff_or_admin(u),
        redirect_field_name=None,
        login_url="/candidate/home#next",
    )(f)


def requires_candidate_coc(f: Callable[..., Any]) -> Callable[..., Any]:
    return user_passes_test(
        lambda u: u_accepted_coc(u) and not is_staff_or_admin(u),
        redirect_field_name=None,
        login_url="/candidate/home#next",
    )(f)


def requires_scholarship_decision(f: Callable[..., Any]) -> Callable[..., Any]:
    return user_passes_test(
        lambda u: u_decided_scholarship(u) and not is_staff_or_admin(u),
        redirect_field_name=None,
        login_url="/candidate/home#next",
    )(f)


def requires_candidate_profile(f: Callable[..., Any]) -> Callable[..., Any]:
    return user_passes_test(
        lambda u: u_has_profile(u) and not is_staff_or_admin(u),
        redirect_field_name=None,
        login_url="/candidate/home#next",
    )(f)


def requires_staff_login(f: Callable[..., Any]) -> Callable[..., Any]:
    return user_passes_test(
        lambda u: u_is_authenticated(u) and is_staff_or_admin(u), redirect_field_name=None, login_url="/account/login"
    )(f)

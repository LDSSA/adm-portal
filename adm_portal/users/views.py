from logging import getLogger

from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError, transaction
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import loader
from django.views.decorators.http import require_http_methods

from interface import interface

from .decorators import requires_candidate_login
from .models import User, UserConfirmEmail, UserResetPassword

logger = getLogger(__name__)


def _get_signup_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        if request.user.is_staff:
            return HttpResponseRedirect("/staff/home")
        return HttpResponseRedirect("/candidate/home")

    if not interface.feature_flag_client.signups_are_open():
        ctx = {"msg": "signup period is over"}
        template = loader.get_template("./user_templates/error.html")
        return HttpResponse(template.render(ctx, request), status=400)

    template = loader.get_template("./user_templates/signup.html")
    return HttpResponse(
        template.render({"logo_url": interface.storage_client.get_url("public-assets/ldssa_logo.png")}, request)
    )


def _post_signup_view(request: HttpRequest) -> HttpResponse:
    if not interface.feature_flag_client.signups_are_open():
        ctx = {"msg": "signup period is over"}
        template = loader.get_template("./user_templates/error.html")
        return HttpResponse(template.render(ctx, request), status=400)

    email = request.POST["email"]
    password = request.POST["password"]

    try:
        user = User.objects.create_user(email=email, password=password)
    except IntegrityError:
        ctx = {"msg": "this e-mail address is already taken", "url": "/account/signup"}
        template = loader.get_template("./user_templates/error.html")
        return HttpResponse(template.render(ctx, request), status=409)

    login(request, user)
    email_confirmation_url = (
        f"{request.get_host()}/account/confirm-email?token={UserConfirmEmail.objects.get(user=user).token}"
    )
    interface.email_client.send_signup_email(to=user.email, email_confirmation_url=email_confirmation_url)
    return HttpResponseRedirect("/candidate/home")


@require_http_methods(["GET", "POST"])
def signup_view(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        return _get_signup_view(request)
    return _post_signup_view(request)


def _get_login_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        if request.user.is_staff:
            return HttpResponseRedirect("/staff/home")
        return HttpResponseRedirect("/candidate/home")

    template = loader.get_template("./user_templates/login.html")
    return HttpResponse(
        template.render({"logo_url": interface.storage_client.get_url("public-assets/ldssa_logo.png")}, request)
    )


def _post_login_view(request: HttpRequest) -> HttpResponse:
    email = request.POST["email"]
    password = request.POST["password"]

    user = authenticate(request, email=email, password=password)
    if user is None:
        ctx = {"msg": "Login Error", "url": "/account/login"}
        template = loader.get_template("./user_templates/error.html")
        return HttpResponse(template.render(ctx, request), status=400)

    login(request, user)

    if user.is_staff:
        return HttpResponseRedirect("/staff/home")
    return HttpResponseRedirect("/candidate/home")


@require_http_methods(["GET", "POST"])
def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        return _get_login_view(request)
    return _post_login_view(request)


# @require_http_methods(["POST"])
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return HttpResponseRedirect("/account/login")


@require_http_methods(["GET"])
def confirm_email_view(request: HttpRequest) -> HttpResponse:
    token = request.GET["token"]
    try:
        user_confirm_email = UserConfirmEmail.objects.get(token=token)
    except UserConfirmEmail.DoesNotExist:
        raise Http404

    with transaction.atomic():
        user = user_confirm_email.user
        user.email_confirmed = True
        user.save()
        user_confirm_email.delete()

    login(request, user)

    return HttpResponseRedirect("/candidate/home")


@require_http_methods(["GET", "POST"])
def start_reset_password_view(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        template = loader.get_template("./user_templates/reset_password_ask_email.html")
        return HttpResponse(template.render({}, request))

    email = request.POST["email"]
    try:
        user = User.objects.get(email=email)
        reset_password, _ = UserResetPassword.objects.get_or_create(user=user)
        reset_password_url = f"{request.get_host()}/account/reset-password?token={reset_password.token}"
        interface.email_client.send_reset_password_email(to=email, reset_password_url=reset_password_url)
    except User.DoesNotExist:
        # we will not disclose that such email is not in our db
        pass

    template = loader.get_template("./user_templates/reset_password_email_sent.html")
    return HttpResponse(template.render({}, request))


@require_http_methods(["GET", "POST"])
def reset_password_view(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        token = request.GET.get("token", "")
        if not UserResetPassword.objects.filter(token=token).count():
            raise Http404
        template = loader.get_template("./user_templates/reset_password.html")
        return HttpResponse(template.render({"token": token}, request))

    token = request.POST["token"]
    password = request.POST["password"]

    try:
        reset_password = UserResetPassword.objects.get(token=token)
    except UserResetPassword.DoesNotExist:
        raise Http404

    user = reset_password.user
    user.set_password(password)
    with transaction.atomic():
        user.save()
        reset_password.delete()
    login(request, user)
    return HttpResponseRedirect("/candidate/home")


@requires_candidate_login
@require_http_methods(["GET"])
def send_confirmation_email_view(request: HttpRequest) -> HttpResponse:
    try:
        email_confirmation_url = (
            f"{request.get_host()}/account/confirm-email?token={UserConfirmEmail.objects.get(user=request.user).token}"
        )
        interface.email_client.send_signup_email(to=request.user.email, email_confirmation_url=email_confirmation_url)
    except UserConfirmEmail.DoesNotExist:
        if request.user.email_confirmed:
            logger.warning(
                f"user `{request.user.email}` requesting confirmation email "
                f"but they are already confirmed.. doing nothing"
            )
        else:
            logger.warning(
                f"user `{request.user.email}` requesting confirmation email "
                f"but they have no confirmation token.. generating new one"
            )
            email_confirmation_url = (
                f"{request.get_host()}/account/confirm-email?token="
                f"{UserConfirmEmail.objects.create(user=request.user).token}"
            )
            interface.email_client.send_signup_email(
                to=request.user.email, email_confirmation_url=email_confirmation_url
            )

    template = loader.get_template("./user_templates/confirmation-email.html")
    return HttpResponse(template.render({"email": request.user.email}, request))

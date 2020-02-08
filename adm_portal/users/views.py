from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.template import loader

from .models import User


def _get_signup_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect("/staff/home")
        return redirect("/candidate/home")

    template = loader.get_template("./user_templates/signup.html")
    return HttpResponse(template.render({}, request))


def _post_signup_view(request: HttpRequest) -> HttpResponse:
    email = request.POST["email"]
    password = request.POST["password"]

    try:
        user = User.objects.create_user(email=email, password=password)
    except IntegrityError:
        ctx = {"msg": "this e-mail address is already taken", "url": "/account/signup"}
        template = loader.get_template("./user_templates/error.html")
        return HttpResponse(template.render(ctx, request), status=409)

    login(request, user)
    # todo: send confirmation email?

    return redirect("/candidate/home")


def signup_view(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        return _get_signup_view(request)
    return _post_signup_view(request)


def _get_login_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect("/staff/home")
        return redirect("/candidate/home")

    template = loader.get_template("./user_templates/login.html")
    return HttpResponse(template.render({}, request))


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
        return redirect("/staff/home")
    return redirect("/candidate/home")


def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        return _get_login_view(request)
    return _post_login_view(request)


# @require_http_methods(["POST"])
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("/account/login")

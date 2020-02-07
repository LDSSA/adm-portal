from typing import Any

from django.contrib import admin
from django.http import HttpRequest, HttpResponse
from django.urls import path

from users.views import login_view, logout_view, signup_view


def todo_view(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
    return HttpResponse(
        f"<html><body><div>Requested {request.path}</div><div>Page is not ready yet!</div></body></html>"
    )


urlpatterns = [
    path("admin/", admin.site.urls),
    # account
    path("account/signup", signup_view, name="accounts-signup"),
    path("account/login", login_view, name="accounts-login"),
    path("account/logout", logout_view, name="accounts-logout"),
    # staff
    path("staff/home", todo_view, name="staff-home"),
    path("staff/profiles", todo_view, name="staff-profiles-list"),
    path("staff/profiles/<int:profile_id>/", todo_view, name="staff-profiles-id"),
    path("staff/applications", todo_view, name="staff-applications-list"),
    path("staff/applications/<int:application_id>", todo_view, name="staff-applications-id"),
    path("staff/payments", todo_view, name="staff-payments-list"),
    path("staff/payments/<int:payment_id>", todo_view, name="staff-payments-id"),
    # candidate
    path("candidate/home", todo_view, name="candidate-home"),
    path("candidate/profile", todo_view, name="candidate-profile"),
    path("candidate/python-test", todo_view, name="candidate-python-test"),
    path("candidate/slu-1", todo_view, name="candidate-slu-1"),
    path("candidate/slu-2", todo_view, name="candidate-slu-2"),
    path("candidate/slu-3", todo_view, name="candidate-slu-3"),
    path("candidate/payment", todo_view, name="candidate-payment"),
]

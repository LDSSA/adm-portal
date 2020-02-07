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
    path("account/signup", signup_view, name="accounts-signup"),
    path("account/login", login_view, name="accounts-login"),
    path("account/logout", logout_view, name="accounts-logout"),
    path("instructor/home", todo_view, name="instructor-home"),
    path("instructor/profiles", todo_view, name="instructor-profiles-list"),
    path("instructor/profiles/<int:profile_id>/", todo_view, name="instructor-profiles-id"),
    path("instructor/applications", todo_view, name="instructor-applications-list"),
    path("instructor/applications/<int:application_id>", todo_view, name="instructor-applications-id"),
    path("instructor/payments", todo_view, name="instructor-payments-list"),
    path("instructor/payments/<int:payment_id>", todo_view, name="instructor-payments-id"),
    path("candidate/home", todo_view, name="candidate-home"),
    path("candidate/profile", todo_view, name="candidate-profile"),
    path("candidate/python-test", todo_view, name="candidate-python-test"),
    path("candidate/slu-1", todo_view, name="candidate-slu-1"),
    path("candidate/slu-2", todo_view, name="candidate-slu-2"),
    path("candidate/slu-3", todo_view, name="candidate-slu-3"),
    path("candidate/payment", todo_view, name="candidate-payment"),
]

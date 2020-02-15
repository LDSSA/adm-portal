from typing import Any, Callable, NamedTuple

from django.contrib import admin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import path

from candidate.application_views import (
    candidate_before_coding_test_view,
    candidate_coding_test_download_view,
    candidate_coding_test_upload_view,
    candidate_coding_test_view,
    candidate_slu_upload_view,
    candidate_slu_view,
    candidate_submission_download_view,
    candidate_submission_feedback_download_view,
)
from candidate.views import candidate_home_view, candidate_profile_edit, candidate_profile_view
from users.decorators import requires_candidate_login, requires_staff_login
from users.views import login_view, logout_view, signup_view


def todo_view(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
    return HttpResponse(
        f"<html><body><div>Requested {request.path}</div><div>Page is not ready yet!</div></body></html>"
    )


class Route(NamedTuple):
    route: str
    view: Callable[..., Any]
    name: str


staff_routes = [
    Route(route="staff/home", view=todo_view, name="staff-home"),
    Route(route="staff/profiles", view=todo_view, name="staff-profiles-list"),
    Route(route="staff/profiles/<int:profile_id>/", view=todo_view, name="staff-profiles-id"),
    Route(route="staff/applications", view=todo_view, name="staff-applications-list"),
    Route(route="staff/applications/<int:application_id>", view=todo_view, name="staff-applications-id"),
    Route(route="staff/payments", view=todo_view, name="staff-payments-list"),
    Route(route="staff/payments/<int:payment_id>", view=todo_view, name="staff-payments-id"),
]

candidate_routes = [
    Route(route="candidate/home", view=candidate_home_view, name="candidate-home"),
    # profile
    Route(route="candidate/profile", view=candidate_profile_view, name="candidate-profile"),
    Route(route="candidate/profile/edit", view=candidate_profile_edit, name="candidate-profile-edit"),
    # coding test
    Route(
        route="candidate/before-coding-test",
        view=candidate_before_coding_test_view,
        name="before-candidate-coding-test",
    ),
    Route(route="candidate/coding-test", view=candidate_coding_test_view, name="candidate-coding-test"),
    Route(
        route="candidate/coding-test/download",
        view=candidate_coding_test_download_view,
        name="candidate-coding-test-download",
    ),
    Route(
        route="candidate/coding-test/upload/",
        view=candidate_coding_test_upload_view,
        name="candidate-coding-test-upload",
    ),
    # slu
    Route(route="candidate/slu/<slug:submission_type>", view=candidate_slu_view, name="candidate-slu"),
    Route(
        route="candidate/slu/upload/<slug:submission_type>",
        view=candidate_slu_upload_view,
        name="candidate-coding-test-upload",
    ),
    # submissions
    Route(
        route="candidate/submission/<slug:submission_type>/<int:submission_id>",
        view=candidate_submission_download_view,
        name="candidate-coding-submission-download",
    ),
    Route(
        route="candidate/submission/feedback/<slug:submission_type>/<int:submission_id>",
        view=candidate_submission_feedback_download_view,
        name="candidate-coding-feedback-download",
    ),
    Route(route="candidate/profile", view=todo_view, name="candidate-profile"),
    Route(route="candidate/payment", view=todo_view, name="candidate-payment"),
]

urlpatterns = [
    path("", lambda req: redirect("account/login")),
    # admin
    path("admin/", admin.site.urls),
    # account
    path("account/login", login_view, name="accounts-login"),
    path("account/logout", logout_view, name="accounts-logout"),
    path("account/signup", signup_view, name="accounts-signup"),
    # staff
    *[path(r.route, requires_staff_login(r.view), name=r.name) for r in staff_routes],
    # candidate
    *[path(r.route, requires_candidate_login(r.view), name=r.name) for r in candidate_routes],
]

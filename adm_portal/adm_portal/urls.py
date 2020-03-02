from typing import Any, Callable, NamedTuple

from django.contrib import admin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import path

from candidate.application_views import (
    candidate_before_coding_test_view,
    candidate_coding_test_download_view,
    candidate_coding_test_view,
    candidate_slu_view,
    candidate_submission_download_view,
    candidate_submission_feedback_download_view,
    candidate_submission_upload_view,
)
from candidate.payments_views import (
    candidate_document_download_view,
    candidate_payment_proof_upload_view,
    candidate_payment_view,
    candidate_student_id_upload_view,
)
from candidate.views import (
    candidate_code_of_conduct_view,
    candidate_home_view,
    candidate_profile_edit,
    candidate_profile_view,
)
from staff.application_views import staff_applications_view
from staff.payment_views import reset_payment_view, staff_payment_view, staff_payments_view
from staff.profile_views import staff_profiles_view
from staff.views import staff_home_view
from users.decorators import requires_candidate_login, requires_staff_login
from users.views import (
    confirm_email_view,
    login_view,
    logout_view,
    reset_password_view,
    signup_view,
    start_reset_password_view,
)


def todo_view(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
    return HttpResponse(
        f"<html><body><div>Requested {request.path}</div><div>Page is not ready yet!</div></body></html>"
    )


class Route(NamedTuple):
    route: str
    view: Callable[..., Any]
    name: str


account_routs = [
    Route(route="account/login", view=login_view, name="accounts-login"),
    Route(route="account/logout", view=logout_view, name="accounts-logout"),
    Route(route="account/signup", view=signup_view, name="accounts-signup"),
    Route(route="account/confirm-email", view=confirm_email_view, name="accounts-confirm-email"),
    Route(route="account/start-reset-password", view=start_reset_password_view, name="accounts-start-reset-password"),
    Route(route="account/reset-password", view=reset_password_view, name="accounts-reset-password"),
]


staff_routes = [
    Route(route="staff/home", view=staff_home_view, name="staff-home"),
    Route(route="staff/profiles", view=staff_profiles_view, name="staff-profiles-list"),
    Route(route="staff/profiles/<int:user_id>/", view=todo_view, name="staff-profile"),
    Route(route="staff/applications", view=staff_applications_view, name="staff-applications-list"),
    Route(route="staff/applications/<int:user_id>", view=todo_view, name="staff-application"),
    Route(route="staff/payments", view=staff_payments_view, name="staff-payments-list"),
    Route(route="staff/payments/<int:user_id>", view=staff_payment_view, name="staff-payment"),
    Route(route="staff/payments/<int:user_id>/reset", view=reset_payment_view, name="staff-reset-payment"),
]

candidate_routes = [
    Route(route="candidate/home", view=candidate_home_view, name="candidate-home"),
    # conde of conduct
    Route(route="candidate/code-of-conduct", view=candidate_code_of_conduct_view, name="candidate-code-of-conduct"),
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
    # slu
    Route(route="candidate/slu/<slug:submission_type>", view=candidate_slu_view, name="candidate-slu"),
    # submissions
    Route(
        route="candidate/submissions/upload/<slug:submission_type>",
        view=candidate_submission_upload_view,
        name="candidate-submissions-upload",
    ),
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
    # payment
    Route(route="candidate/payment", view=candidate_payment_view, name="candidate-payment"),
    Route(
        route="candidate/payment/download-document/<int:document_id>",
        view=candidate_document_download_view,
        name="candidate-payment-document-download",
    ),
    Route(
        route="candidate/payment/upload-payment-proof",
        view=candidate_payment_proof_upload_view,
        name="candidate-payment-proof-upload",
    ),
    Route(
        route="candidate/payment/upload-student-id",
        view=candidate_student_id_upload_view,
        name="candidate-student-id-upload",
    ),
]

urlpatterns = [
    path("", lambda req: redirect("account/login")),
    # admin
    path("admin/", admin.site.urls),
    # account
    *[path(r.route, r.view, name=r.name) for r in account_routs],
    # staff
    *[path(r.route, requires_staff_login(r.view), name=r.name) for r in staff_routes],
    # candidate
    *[path(r.route, requires_candidate_login(r.view), name=r.name) for r in candidate_routes],
]

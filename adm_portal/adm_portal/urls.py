import json
import time
from typing import Any, Callable, NamedTuple

from django.contrib import admin
from django.contrib.auth import authenticate
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from candidate.application_views import (
    candidate_assignment_download_view,
    candidate_before_coding_test_view,
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
from candidate.profile_views import candidate_profile_view
from candidate.views import candidate_code_of_conduct_view, candidate_home_view, candidate_scholarship_view
from staff.application_views import staff_applications_view
from staff.candidates_views import staff_candidate_view, staff_candidates_view
from staff.events_view import staff_events_view
from staff.interview_views import staff_interview_view, staff_interviews_view
from staff.payment_views import reset_payment_view, staff_payment_view, staff_payments_view
from staff.selection_views import (
    staff_draw_candidates_view,
    staff_reject_selection_view,
    staff_select_candidates_view,
    staff_selection_candidates_view,
)
from staff.views import staff_home_view
from users.decorators import (
    requires_candidate_coc,
    requires_candidate_confirmed,
    requires_candidate_login,
    requires_candidate_profile,
    requires_scholarship_decision,
    requires_staff_login,
)
from users.views import (
    confirm_email_view,
    login_view,
    logout_view,
    reset_password_view,
    send_confirmation_email_view,
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
    Route(
        route="account/send-confirmation-email",
        view=send_confirmation_email_view,
        name="accounts-send-confirmation-email",
    ),
]


staff_routes = [
    Route(route="staff/home", view=staff_home_view, name="staff-home"),
    Route(route="staff/events", view=staff_events_view, name="staff-events"),
    Route(route="staff/candidates", view=staff_candidates_view, name="staff-profiles-list"),
    Route(route="staff/candidates/<int:user_id>/", view=staff_candidate_view, name="staff-profile"),
    Route(route="staff/applications", view=staff_applications_view, name="staff-applications-list"),
    Route(route="staff/applications/<int:user_id>", view=todo_view, name="staff-application"),
    Route(route="staff/selections/", view=staff_selection_candidates_view, name="staff-selections"),
    Route(route="staff/selections-selected/", view=todo_view, name="staff-selections-selected"),
    Route(route="staff/selections/draw", view=staff_draw_candidates_view, name="staff-selections-draw"),
    Route(
        route="staff/selections/reject-draw/<int:candidate_id>",
        view=staff_reject_selection_view,
        name="staff-selections-candidates-reject-draw",
    ),
    Route(route="staff/selections/select", view=staff_select_candidates_view, name="staff-selections-select"),
    Route(route="staff/interviews", view=staff_interviews_view, name="staff-interviews-list"),
    Route(route="staff/interviews/<int:user_id>", view=staff_interview_view, name="staff-interview"),
    Route(route="staff/payments", view=staff_payments_view, name="staff-payments-list"),
    Route(route="staff/payments/<int:user_id>", view=staff_payment_view, name="staff-payment"),
    Route(route="staff/payments/<int:user_id>/reset", view=reset_payment_view, name="staff-reset-payment"),
]

candidate_routes = [Route(route="candidate/home", view=candidate_home_view, name="candidate-home")]

confirmed_candidate_routes = [
    # code of conduct
    Route(route="candidate/code-of-conduct", view=candidate_code_of_conduct_view, name="candidate-code-of-conduct")
]

coc_candidate_routes = [
    # scholarship
    Route(route="candidate/scholarship", view=candidate_scholarship_view, name="candidate-scholarship")
]

scholarship_candidate_routes = [
    # profile
    Route(route="candidate/profile", view=candidate_profile_view, name="candidate-profile")
]

candidate_with_profile_routes = [
    # coding test
    Route(
        route="candidate/before-coding-test",
        view=candidate_before_coding_test_view,
        name="before-candidate-coding-test",
    ),
    Route(route="candidate/coding-test", view=candidate_coding_test_view, name="candidate-coding-test"),
    # slu
    Route(route="candidate/slu/<slug:submission_type>", view=candidate_slu_view, name="candidate-slu"),
    # submissions
    Route(
        route="candidate/assignment-download",
        view=candidate_assignment_download_view,
        name="candidate-assignment-download",
    ),
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


@csrf_exempt
def sleep(request: HttpRequest, duration: int) -> HttpResponse:
    if request.method != "POST":
        return JsonResponse(status=404, data={})

    payload = json.loads(request.body.decode("utf-8"))
    user = authenticate(request, email=payload.get("email", ""), password=payload.get("password", ""))
    try:
        if not user.is_admin:
            raise Exception
    except Exception:
        return JsonResponse(status=404, data={})

    time.sleep(duration)
    return JsonResponse(status=200, data={"duration": duration})


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
    *[path(r.route, requires_candidate_confirmed(r.view), name=r.name) for r in confirmed_candidate_routes],
    *[path(r.route, requires_candidate_coc(r.view), name=r.name) for r in coc_candidate_routes],
    *[path(r.route, requires_scholarship_decision(r.view), name=r.name) for r in scholarship_candidate_routes],
    *[path(r.route, requires_candidate_profile(r.view), name=r.name) for r in candidate_with_profile_routes],
    path("loadtest/sleep/<int:duration>", sleep, name="loadtest-sleep"),
]

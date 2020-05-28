from datetime import datetime

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import loader
from django.views.decorators.http import require_http_methods

from applications.domain import Status
from interface import interface
from profiles.models import Profile
from selection.status import SelectionStatus

from .domain import Domain
from .helpers import build_context


@require_http_methods(["GET"])
def candidate_home_view(request: HttpRequest) -> HttpResponse:
    template = loader.get_template("./candidate_templates/home.html")
    state = Domain.get_candidate_state(request.user)

    # the action_point is the first open section in the steps accordion
    # accordion_enabled_status say whether each accordion section should be enabled
    accordion_enabled_status = {
        "confirmed_email": False,
        "accepted_coc": False,
        "decided_scholarship": False,
        "created_profile": False,
        "admission_test": False,
        "selection_results": False,
        "payment": False,
    }

    if not state.confirmed_email:
        action_point = "confirmed_email"
        accordion_enabled_status["confirmed_email"] = True

    elif not state.accepted_coc:
        action_point = "accepted_coc"
        accordion_enabled_status["confirmed_email"] = True
        accordion_enabled_status["accepted_coc"] = True

    elif not state.decided_scholarship:
        action_point = "decided_scholarship"
        accordion_enabled_status["confirmed_email"] = True
        accordion_enabled_status["accepted_coc"] = True
        accordion_enabled_status["decided_scholarship"] = True

    elif not state.created_profile:
        action_point = "created_profile"
        accordion_enabled_status["confirmed_email"] = True
        accordion_enabled_status["accepted_coc"] = True
        accordion_enabled_status["decided_scholarship"] = True
        accordion_enabled_status["created_profile"] = True

    elif state.application_status != Status.passed or state.selection_status is None:
        action_point = "admission_test"
        accordion_enabled_status["confirmed_email"] = True
        accordion_enabled_status["accepted_coc"] = True
        accordion_enabled_status["decided_scholarship"] = True
        accordion_enabled_status["created_profile"] = True
        accordion_enabled_status["admission_test"] = True

    elif (
        state.selection_status is not None and state.selection_status not in SelectionStatus.SELECTION_POSITIVE_STATUS
    ):
        action_point = "selection_results"
        accordion_enabled_status["confirmed_email"] = True
        accordion_enabled_status["accepted_coc"] = True
        accordion_enabled_status["decided_scholarship"] = True
        accordion_enabled_status["created_profile"] = True
        accordion_enabled_status["admission_test"] = True
        accordion_enabled_status["selection_results"] = True

    else:
        action_point = "payment"
        accordion_enabled_status["confirmed_email"] = True
        accordion_enabled_status["accepted_coc"] = True
        accordion_enabled_status["decided_scholarship"] = True
        accordion_enabled_status["created_profile"] = True
        accordion_enabled_status["admission_test"] = True
        accordion_enabled_status["selection_results"] = True
        accordion_enabled_status["payment"] = True

    first_name = None
    if state.created_profile:
        first_name = request.user.profile.full_name.split(" ")[0]

    ctx = build_context(
        request.user,
        {
            "user": request.user,
            "state": state,
            "selection_status_values": SelectionStatus,
            "action_point": action_point,
            "first_name": first_name,
            "is_applications_open": datetime.now() >= interface.feature_flag_client.get_applications_opening_date(),
            "applications_open_datetime": interface.feature_flag_client.get_applications_opening_date().strftime(
                "%Y-%m-%d %H:%M"
            ),
            "applications_close_datetime": interface.feature_flag_client.get_applications_closing_date().strftime(
                "%Y-%m-%d %H:%M"
            ),
            "applications_close_date": interface.feature_flag_client.get_applications_closing_date().strftime(
                "%Y-%m-%d"
            ),
            "coding_test_duration": interface.feature_flag_client.get_coding_test_duration() / 60,
            "accordion_enabled_status": accordion_enabled_status,
        },
    )
    return HttpResponse(template.render(ctx, request))


@require_http_methods(["GET", "POST"])
def candidate_code_of_conduct_view(request: HttpRequest) -> HttpResponse:
    user = request.user
    if request.method == "GET":
        template = loader.get_template("./candidate_templates/code_of_conduct.html")
        ctx = build_context(user, {"code_of_conduct_accepted": user.code_of_conduct_accepted})
        return HttpResponse(template.render(ctx, request))

    user.code_of_conduct_accepted = True
    user.save()

    return HttpResponseRedirect("/candidate/home")


@require_http_methods(["GET", "POST"])
def candidate_scholarship_view(request: HttpRequest) -> HttpResponse:
    user = request.user
    if request.method == "GET":
        template = loader.get_template("./candidate_templates/scholarship.html")
        ctx = build_context(
            request.user,
            {
                "decision_made": user.applying_for_scholarship is not None,
                "applying_for_scholarship": user.applying_for_scholarship,
            },
        )
        return HttpResponse(template.render(ctx, request))

    user.applying_for_scholarship = request.POST["decision"] == "yes"
    user.save()

    return HttpResponseRedirect("/candidate/home")


@require_http_methods(["GET", "POST"])
def candidate_contactus_view(request: HttpRequest) -> HttpResponse:
    user = request.user
    if request.method == "GET":
        template = loader.get_template("./candidate_templates/contactus.html")
        ctx = build_context(request.user)
        return HttpResponse(template.render(ctx, request))

    user_url = f"{request.get_host()}/staff/candidates/{user.id}/"
    message = request.POST["message"]
    try:
        user_name = user.profile.full_name
    except Profile.DoesNotExist:
        user_name = "-"

    interface.email_client.send_contact_us_email(
        from_email=user.email, user_name=user_name, user_url=user_url, message=message
    )
    user.save()

    template = loader.get_template("./candidate_templates/contactus-success.html")
    ctx = build_context(request.user)
    return HttpResponse(template.render(ctx, request))

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import loader
from django.views.decorators.http import require_http_methods

from applications.domain import Status
from interface import interface
from selection.status import SelectionStatus

from .domain import Domain
from .helpers import build_context


@require_http_methods(["GET"])
def candidate_home_view(request: HttpRequest) -> HttpResponse:
    template = loader.get_template("./candidate_templates/home.html")
    state = Domain.get_candidate_state(request.user)

    if not state.confirmed_email:
        action_point = "confirmed_email"
    elif not state.accepted_coc:
        action_point = "accepted_coc"
    elif not state.created_profile:
        action_point = "created_profile"
    elif state.application_status != Status.passed or state.selection_status is None:
        action_point = "admission_test"
    elif (
        state.selection_status is not None and state.selection_status not in SelectionStatus.SELECTION_POSITIVE_STATUS
    ):
        action_point = "selection_results"
    else:
        action_point = "payment"

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
            "applications_close_datetime": interface.feature_flag_client.get_applications_closing_date().strftime(
                "%Y-%m-%d %H:%M"
            ),
            "applications_close_date": interface.feature_flag_client.get_applications_closing_date().strftime(
                "%Y-%m-%d"
            ),
            "coding_test_duration": interface.feature_flag_client.get_coding_test_duration() / 60,
        },
    )
    return HttpResponse(template.render(ctx, request))


@require_http_methods(["GET", "POST"])
def candidate_code_of_conduct_view(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        template = loader.get_template("./candidate_templates/code_of_conduct.html")
        ctx = build_context(request.user, {"code_of_conduct_accepted": request.user.code_of_conduct_accepted})
        return HttpResponse(template.render(ctx, request))

    request.user.code_of_conduct_accepted = True
    request.user.save()

    return HttpResponseRedirect("/candidate/home")

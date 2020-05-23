from typing import Tuple

from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import loader
from django.views.decorators.http import require_http_methods

from interface import interface
from selection.domain import SelectionDomain
from selection.logs import get_selection_logs
from selection.models import Selection
from selection.payment import add_note, load_payment_data
from selection.queries import SelectionQueries
from selection.status import SelectionStatus
from users.models import User


@require_http_methods(["GET"])
def staff_interviews_view(request: HttpRequest) -> HttpResponse:
    ctx = {
        "selections": SelectionQueries.filter_by_status_in([SelectionStatus.INTERVIEW]),
        "selection_status": SelectionStatus,
    }
    template = loader.get_template("./staff_templates/interviews.html")
    return HttpResponse(template.render(ctx, request))


@require_http_methods(["GET", "POST"])
def staff_interview_view(request: HttpRequest, user_id: int) -> HttpResponse:
    _, selection = _get_user_selection(user_id)
    if request.method == "GET":
        return _get_staff_interview_view(request, selection, user_id)
    return _post_staff_interview_view(request, selection)


def _get_user_selection(user_id: int) -> Tuple[User, Selection]:
    try:
        candidate = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise Http404

    try:
        selection = Selection.objects.get(user=candidate)
    except User.DoesNotExist:
        raise Http404

    return candidate, selection


def _get_staff_interview_view(request: HttpRequest, selection: Selection, candidate_id: int) -> HttpResponse:
    if SelectionDomain.get_status(selection) != SelectionStatus.INTERVIEW:
        return HttpResponseRedirect("/staff/interviews")

    ctx = {"s": selection, "candidate_id": candidate_id, "logs": get_selection_logs(selection)}
    template = loader.get_template("./staff_templates/interview_id.html")
    return HttpResponse(template.render(ctx, request))


def _post_staff_interview_view(request: HttpRequest, selection: Selection) -> HttpResponse:
    staff_user = request.user
    action = request.POST["action"]
    msg = request.POST.get("msg", None)

    if action == "note":
        add_note(selection, msg, staff_user)
    elif action == "reject":
        SelectionDomain.manual_update_status(selection, SelectionStatus.REJECTED, staff_user, msg=msg)
        interface.email_client.send_interview_failed_email(to=selection.user.email, message=msg)
    elif action == "accept":
        SelectionDomain.manual_update_status(selection, SelectionStatus.SELECTED, staff_user, msg=msg)
        load_payment_data(selection)
        interface.email_client.send_interview_passed_email(to=selection.user.email)

    return _get_staff_interview_view(request, selection, selection.user.id)

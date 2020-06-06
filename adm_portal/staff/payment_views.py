from typing import Tuple

from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import loader
from django.views.decorators.http import require_http_methods

from interface import interface
from selection.domain import SelectionDomain
from selection.logs import get_selection_logs
from selection.models import Selection
from selection.payment import add_note, can_be_updated, load_payment_data
from selection.queries import SelectionQueries
from selection.status import SelectionStatus
from users.models import User


@require_http_methods(["GET"])
def staff_payments_view(request: HttpRequest) -> HttpResponse:
    ctx = {
        "selections": SelectionQueries.filter_by_status_in(
            [
                SelectionStatus.SELECTED,
                SelectionStatus.TO_BE_ACCEPTED,
                SelectionStatus.ACCEPTED,
                SelectionStatus.REJECTED,
            ]
        ),
        "selection_status": SelectionStatus,
    }
    template = loader.get_template("./staff_templates/payments.html")
    return HttpResponse(template.render(ctx, request))


@require_http_methods(["GET", "POST"])
def staff_payment_view(request: HttpRequest, user_id: int) -> HttpResponse:
    _, selection = _get_user_selection(user_id)
    if request.method == "GET":
        return _get_staff_payment_view(request, selection, user_id)
    return _post_staff_payment_view(request, selection)


@require_http_methods(["POST"])
def reset_payment_view(request: HttpRequest, user_id: int) -> HttpResponse:
    _, selection = _get_user_selection(user_id)
    try:
        load_payment_data(selection, request.user)
        SelectionDomain.update_status(selection, SelectionStatus.SELECTED, user=request.user)
    except Exception:
        raise Http404

    return HttpResponseRedirect(f"/staff/payments/{user_id}")


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


def _get_staff_payment_view(request: HttpRequest, selection: Selection, candidate_id: int) -> HttpResponse:
    ctx = {
        "s": selection,
        "selection_status": SelectionStatus,
        "can_update": can_be_updated(selection),
        "candidate_id": candidate_id,
        "docs": [
            {
                "url": interface.storage_client.get_url(doc.file_location, content_type="image"),
                "doc_type": doc.doc_type,
                "created_at": doc.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for doc in selection.documents.all().order_by("-created_at")
        ],
        "logs": get_selection_logs(selection),
    }
    template = loader.get_template("./staff_templates/payment_id.html")
    return HttpResponse(template.render(ctx, request))


def _post_staff_payment_view(request: HttpRequest, selection: Selection) -> HttpResponse:
    staff_user = request.user
    action = request.POST["action"]
    msg = request.POST.get("msg", None)

    if action == "note":
        add_note(selection, msg, staff_user)
    elif action == "reject":
        SelectionDomain.manual_update_status(selection, SelectionStatus.REJECTED, staff_user, msg=msg)
        interface.email_client.send_payment_refused_proof_email(
            to_email=selection.user.email, to_name=selection.user.profile.name, message=msg
        )
    elif action == "ask_additional":
        SelectionDomain.manual_update_status(selection, SelectionStatus.SELECTED, staff_user, msg=msg)
        interface.email_client.send_payment_need_additional_proof_email(
            to_email=selection.user.email, to_name=selection.user.profile.name, message=msg
        )
    elif action == "accept":
        SelectionDomain.manual_update_status(selection, SelectionStatus.ACCEPTED, staff_user, msg=msg)
        interface.email_client.send_payment_accepted_proof_email(
            to_email=selection.user.email, to_name=selection.user.profile.name, message=msg
        )

    return _get_staff_payment_view(request, selection, selection.user.id)

from typing import Tuple

from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import loader
from django.views.decorators.http import require_http_methods

from interface import interface
from payments.domain import Domain, DomainException, DomainQueries
from payments.models import Payment
from users.models import User


@require_http_methods(["GET"])
def staff_payments_view(request: HttpRequest) -> HttpResponse:
    ctx = {"payments": Payment.objects.all().order_by("user__email")}
    template = loader.get_template("./staff_templates/payments.html")
    return HttpResponse(template.render(ctx, request))


@require_http_methods(["GET", "POST"])
def staff_payment_view(request: HttpRequest, user_id: int) -> HttpResponse:
    _, payment = _get_user_payment(user_id)
    if request.method == "GET":
        return _get_staff_payment_view(request, payment, user_id)
    return _post_staff_payment_view(request, payment)


@require_http_methods(["POST"])
def reset_payment_view(request: HttpRequest, user_id: int) -> HttpResponse:
    _, payment = _get_user_payment(user_id)
    try:
        Domain.reset_payment(payment, request.user)
    except DomainException:
        raise Http404

    return HttpResponseRedirect(f"/staff/payments/{user_id}")


def _get_user_payment(user_id: int) -> Tuple[User, Payment]:
    try:
        candidate = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise Http404

    try:
        payment = Payment.objects.get(user=candidate)
    except User.DoesNotExist:
        raise Http404

    return candidate, payment


def _get_staff_payment_view(request: HttpRequest, payment: Payment, candidate_id: int) -> HttpResponse:
    ctx = {
        "payment": payment,
        "can_reset": Domain.can_reset_payment(payment),
        "candidate_id": candidate_id,
        "docs": [
            {
                "url": interface.storage_client.get_url(doc.file_location, content_type="image"),
                "doc_type": doc.doc_type,
            }
            for doc in payment.documents.all()
        ],
        "logs": DomainQueries.get_payment_logs(payment),
    }
    template = loader.get_template("./staff_templates/payment_id.html")
    return HttpResponse(template.render(ctx, request))


def _post_staff_payment_view(request: HttpRequest, payment: Payment) -> HttpResponse:
    staff_user = request.user
    action = request.POST["action"]
    msg = request.POST.get("msg", None)

    if action == "note":
        Domain.add_payment_note(payment, msg, staff_user)
    elif action == "reject":
        Domain.manual_update_status(payment, "rejected", staff_user, msg=msg)
        interface.email_client.send_payment_refused_proof_email(to=payment.user.email, msg=msg)
    elif action == "ask_additional":
        Domain.manual_update_status(payment, "waiting_for_documents", staff_user, msg=msg)
        interface.email_client.send_payment_need_additional_proof_email(to=payment.user.email, msg=msg)
    elif action == "accept":
        Domain.manual_update_status(payment, "accepted", staff_user, msg=msg)
        interface.email_client.send_payment_accepted_proof_email(to=payment.user.email, msg=msg)

    return _get_staff_payment_view(request, payment, payment.user.id)

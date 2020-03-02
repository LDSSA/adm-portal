from typing import Tuple

from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import loader
from django.views.decorators.http import require_http_methods

from interface import interface
from payments.domain import Domain, DomainException
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
    candidate, payment = _get_user_payment(user_id)
    try:
        Domain.reset_payment(payment, candidate.profile)
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
    }
    template = loader.get_template("./staff_templates/payment_id.html")
    return HttpResponse(template.render(ctx, request))


def _post_staff_payment_view(request: HttpRequest, payment: Payment) -> HttpResponse:
    action = request.POST["action"]
    if action == "reject":
        msg = request.POST["action"]
        payment.status = "rejected"
        payment.save()
        interface.email_client.send_payment_refused_proof_email(to=payment.user.email, msg=msg)
    elif action == "ask_additional":
        msg = request.POST["action"]
        payment.status = "waiting_for_documents"
        payment.save()
        interface.email_client.send_payment_need_additional_proof_email(to=payment.user.email, msg=msg)
    elif action == "accept":
        msg = request.POST.get("action")
        payment.status = "accepted"
        payment.save()
        interface.email_client.send_payment_accepted_proof_email(to=payment.user.email, msg=msg)

    return _get_staff_payment_view(request, payment)

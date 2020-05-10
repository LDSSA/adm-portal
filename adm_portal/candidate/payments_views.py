from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import loader
from django.views.decorators.http import require_http_methods

from interface import interface
from payments.domain import Domain
from payments.models import Document, Payment
from storage_client import StorageClient

from .helpers import build_context


def candidate_payment_view(request: HttpRequest) -> HttpResponse:
    try:
        payment = request.user.payment
    except Payment.DoesNotExist:
        return HttpResponse("This candidate has no payment!")

    payment_proofs = payment.get_payment_proof_documents
    student_ids = payment.get_student_id_documents

    template = loader.get_template("./candidate_templates/payment.html")

    context = {
        "payment": payment,
        "can_update": Domain.payment_can_be_updated(payment),
        "profile": request.user.profile,
        "payment_proofs": payment_proofs,
        "student_ids": student_ids,
    }
    context = build_context(request.user, context)

    return HttpResponse(template.render(context, request))


@require_http_methods(["GET"])
def candidate_document_download_view(request: HttpRequest, document_id: int) -> HttpResponse:
    payment = Payment.objects.get(user=request.user)
    document = Document.objects.get(id=document_id, payment=payment)
    url = interface.storage_client.get_attachment_url(document.file_location)

    return HttpResponseRedirect(url)


@require_http_methods(["POST"])
def candidate_payment_proof_upload_view(request: HttpRequest) -> HttpResponse:
    return _candidate_document_upload(request, document_type="payment_proof")


@require_http_methods(["POST"])
def candidate_student_id_upload_view(request: HttpRequest) -> HttpResponse:
    return _candidate_document_upload(request, document_type="student_id")


def _candidate_document_upload(request: HttpRequest, document_type: str) -> HttpResponse:
    f = request.FILES["file"]
    upload_key = f"payments/{document_type}/{request.user.uuid}/{f.name}"
    upload_key_unique = StorageClient.key_append_uuid(upload_key)

    interface.storage_client.save(upload_key_unique, f)

    document = Document(file_location=upload_key_unique, doc_type=document_type)
    payment = Payment.objects.get(user=request.user)
    Domain.add_document(payment, document)

    return HttpResponseRedirect("/candidate/payment")

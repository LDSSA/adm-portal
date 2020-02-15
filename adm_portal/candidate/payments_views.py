from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import loader
from django.views.decorators.http import require_http_methods

from interface import get_storage_client
from payments.models import Document, Payment
from profiles.models import Profile
from storage_client import StorageClient


def candidate_payment_view(request: HttpRequest) -> HttpResponse:
    payment = Payment.objects.filter(user=request.user).first()
    if not payment:
        return HttpResponse("This candidate has no payment!")

    profile = Profile.objects.get(user=request.user)

    payment_proofs = payment.get_payment_proof_documents
    student_ids = payment.get_student_id_documents

    template = loader.get_template("./candidate_templates/payment.html")
    context = {"payment": payment, "profile": profile, "payment_proofs": payment_proofs, "student_ids": student_ids}

    return HttpResponse(template.render(context, request))


@require_http_methods(["GET"])
def candidate_document_download_view(request: HttpRequest, document_id: int) -> HttpResponse:
    payment = Payment.objects.get(user=request.user)
    document = Document.objects.get(id=document_id, payment=payment)
    url = get_storage_client().get_attachment_url(document.file_location)

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

    get_storage_client().save(upload_key_unique, f)

    document = Document(file_location=upload_key_unique, doc_type=document_type)
    payment = Payment.objects.get(user=request.user)
    payment.add_document(document)

    return HttpResponseRedirect("/candidate/payment")

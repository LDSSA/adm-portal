from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import loader
from django.views.decorators.http import require_http_methods

from interface import interface
from selection.domain import SelectionDomain
from selection.models import Selection, SelectionDocument
from selection.payment import add_document, can_be_updated
from selection.queries import SelectionDocumentQueries
from selection.status import SelectionStatus

from .helpers import build_context


def _get_candidate_payment_view(request: HttpRequest) -> HttpResponse:
    try:
        selection = request.user.selection
    except Selection.DoesNotExist:
        raise Http404

    payment_proofs = SelectionDocumentQueries.get_payment_proof_documents(selection)
    student_ids = SelectionDocumentQueries.get_student_id_documents(selection)

    template = loader.get_template("./candidate_templates/payment.html")

    context = {
        "s": selection,
        "selection_status": SelectionStatus,
        "can_update": can_be_updated(selection),
        "profile": request.user.profile,
        "payment_proofs": payment_proofs,
        "student_ids": student_ids,
    }
    context = build_context(request.user, context)

    return HttpResponse(template.render(context, request))


def _post_candidate_payment_view(request: HttpRequest) -> HttpResponse:
    try:
        selection = request.user.selection
    except Selection.DoesNotExist:
        raise Http404
    SelectionDomain.manual_update_status(selection, SelectionStatus.TO_BE_ACCEPTED, request.user)
    return HttpResponseRedirect("/candidate/payment")


@require_http_methods(["GET", "POST"])
def candidate_payment_view(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        return _get_candidate_payment_view(request)
    return _post_candidate_payment_view(request)


@require_http_methods(["GET"])
def candidate_document_download_view(request: HttpRequest, document_id: int) -> HttpResponse:
    try:
        selection = request.user.selection
        document = SelectionDocument.objects.get(selection=selection, id=document_id)
    except (Selection.DoesNotExist, SelectionDocument):
        raise Http404
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
    upload_key_unique = interface.storage_client.key_append_uuid(upload_key)

    interface.storage_client.save(upload_key_unique, f)

    document = SelectionDocument(file_location=upload_key_unique, doc_type=document_type)
    selection = request.user.selection
    add_document(selection, document)

    return HttpResponseRedirect("/candidate/payment")

from datetime import datetime
from typing import Any, Dict

from django.conf import settings
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import loader
from django.views.decorators.http import require_http_methods

from applications.domain import Domain
from applications.models import Application, Submission, SubmissionType, SubmissionTypes
from interface import interface

from .helpers import build_context

# coding test views


@require_http_methods(["GET", "POST"])
def candidate_before_coding_test_view(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        template = loader.get_template("./candidate_templates/before_coding_test.html")
        context = build_context(request.user)
        return HttpResponse(template.render(context, request))

    application = Application.objects.get(user=request.user)
    if application.coding_test_started_at is None:
        application.coding_test_started_at = datetime.now()
        application.save()

    return HttpResponseRedirect("/candidate/coding-test")


@require_http_methods(["GET"])
def candidate_coding_test_view(request: HttpRequest) -> HttpResponse:
    application, _ = Application.objects.get_or_create(user=request.user)
    if application.coding_test_started_at is None:
        return HttpResponseRedirect("/candidate/before-coding-test")

    submission_type_ = SubmissionTypes.coding_test
    ctx = build_context(request.user, submission_view_ctx(application, submission_type_))
    template = loader.get_template("./candidate_templates/coding_test.html")
    return HttpResponse(template.render(ctx, request))


@require_http_methods(["GET"])
def candidate_coding_test_download_view(request: HttpRequest) -> HttpResponse:
    url = interface.storage_client.get_attachment_url("coding_test.ipynb", content_type="application/vnd.jupyter")
    application = Application.objects.get(user=request.user)
    if application.coding_test_started_at is None:
        application.coding_test_started_at = datetime.now()
        application.save()

    return HttpResponseRedirect(url)


# slu views


@require_http_methods(["GET"])
def candidate_slu_view(request: HttpRequest, submission_type: str) -> HttpResponse:
    application, _ = Application.objects.get_or_create(user=request.user)
    submission_type_ = getattr(SubmissionTypes, submission_type)
    ctx = build_context(request.user, submission_view_ctx(application, submission_type_))
    template = loader.get_template("./candidate_templates/slu.html")
    return HttpResponse(template.render(ctx, request))


@require_http_methods(["POST"])
def candidate_submission_upload_view(request: HttpRequest, submission_type: str) -> HttpResponse:
    submission_type_ = getattr(SubmissionTypes, submission_type)

    file = request.FILES["file"]
    now_str = datetime.now().strftime("%m_%d_%Y__%H_%M_%S")
    upload_key = f"{submission_type_.uname}/{request.user.uuid}/{file.name}@{now_str}"
    interface.storage_client.save(upload_key, file)

    submission_result = interface.grader_client.grade(
        assignment_id=submission_type_.uname,
        user_uuid=request.user.uuid,
        submission_s3_bucket=settings.STORAGE_CLIENT_NAMESPACE,
        submission_s3_key=upload_key,
    )

    application = Application.objects.get(user=request.user)
    sub = Submission(
        file_location=upload_key, score=submission_result.score, feedback_location=submission_result.feedback_s3_key
    )
    Domain.add_submission(application, submission_type_, sub)

    return HttpResponseRedirect(f"/candidate/slu/{submission_type}")


# generic


def submission_view_ctx(application: Application, submission_type: SubmissionType) -> Dict[str, Any]:
    return {
        "submission_type": submission_type,
        "status": Domain.get_sub_type_status(application, submission_type).name,
        "submissions_closes_at": Domain.get_close_date(application, submission_type),
        "best_score": Domain.get_best_score(application, submission_type),
        "download_enabled": Domain.can_add_submission(application, submission_type),
        "upload_enabled": Domain.can_add_submission(application, submission_type),
        "submissions": Submission.objects.filter(
            application=application, submission_type=submission_type.uname
        ).order_by("-updated_at"),
    }


@require_http_methods(["GET"])
def candidate_submission_download_view(request: HttpRequest, submission_type: str, submission_id: int) -> HttpResponse:
    try:
        submission: Submission = Submission.objects.get(
            id=submission_id, submission_type=submission_type, application=request.user.application
        )
    except Submission.DoesNotExist:
        raise Http404
    url = interface.storage_client.get_attachment_url(submission.file_location, content_type="application/vnd.jupyter")

    return HttpResponseRedirect(url)


@require_http_methods(["GET"])
def candidate_submission_feedback_download_view(
    request: HttpRequest, submission_type: str, submission_id: int
) -> HttpResponse:
    try:
        submission: Submission = Submission.objects.get(
            id=submission_id, submission_type=submission_type, application=request.user.application
        )
    except Submission.DoesNotExist:
        raise Http404
    url = interface.storage_client.get_url(submission.feedback_location, content_type="text/html")

    return HttpResponseRedirect(url)

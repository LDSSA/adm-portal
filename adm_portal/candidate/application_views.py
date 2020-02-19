from datetime import datetime

from django.conf import settings
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import loader
from django.views.decorators.http import require_http_methods

from applications.models import Application, Submission, SubmissionTypes
from interface import interface

# coding test views


@require_http_methods(["GET", "POST"])
def candidate_before_coding_test_view(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        template = loader.get_template("./candidate_templates/before_coding_test.html")
        return HttpResponse(template.render({}, request))

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

    submission_type = SubmissionTypes.coding_test
    ctx = {
        "submission_type": submission_type,
        "status": application.coding_test_status,
        "submissions_closes_at": application.coding_test_submission_closes_at,
        "passed": application.coding_test_passed,
        "failed": (not application.coding_test_passed and not application.coding_test_submission_is_open),
        "best_score": application.coding_test_best_score,
        "download_enabled": True,  # todo use feature flag?
        "upload_enabled": (
            application.coding_test_submission_is_open and interface.feature_flag_client.accepting_test_submissions()
        ),
        "submissions": Submission.objects.filter(
            application=application, submission_type=submission_type.uname
        ).order_by("-updated_at"),
    }
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


@require_http_methods(["POST"])
def candidate_coding_test_upload_view(request: HttpRequest) -> HttpResponse:
    file = request.FILES["file"]
    submission_type = "coding_test"
    now_str = datetime.now().strftime("%m_%d_%Y__%H_%M_%S")
    upload_key = f"{submission_type}/{request.user.uuid}/{file.name}@{now_str}"
    interface.storage_client.save(upload_key, file)

    submission_result = interface.grader_client.grade(
        assignment_id=submission_type,
        user_uuid=request.user.uuid,
        submission_s3_bucket=settings.STORAGE_CLIENT_NAMESPACE,
        submission_s3_key=upload_key,
    )

    submission = Submission(
        file_location=upload_key, score=submission_result.score, feedback_location=submission_result.feedback_s3_key
    )
    application = Application.objects.get(user=request.user)
    application.coding_test_new_submission(submission)

    return HttpResponseRedirect("/candidate/coding-test")


# slu views


@require_http_methods(["GET"])
def candidate_slu_view(request: HttpRequest, submission_type: str) -> HttpResponse:
    application, _ = Application.objects.get_or_create(user=request.user)

    submission_type_ = getattr(SubmissionTypes, submission_type)

    ctx = {
        "submission_type": submission_type_,
        "passed": application.query_passed(submission_type_),
        "failed": False,  # todo use feature flag?
        "best_score": application.query_best_score(submission_type_),
        "upload_enabled": True,  # todo use feature flag,
        "submissions": Submission.objects.filter(
            application=application, submission_type=submission_type_.uname
        ).order_by("-updated_at"),
    }
    template = loader.get_template("./candidate_templates/slu.html")
    return HttpResponse(template.render(ctx, request))


@require_http_methods(["POST"])
def candidate_slu_upload_view(request: HttpRequest, submission_type: str) -> HttpResponse:
    file = request.FILES["file"]
    now_str = datetime.now().strftime("%m_%d_%Y__%H_%M_%S")
    upload_key = f"{submission_type}/{request.user.uuid}/{file.name}@{now_str}"
    interface.storage_client.save(upload_key, file)

    submission_result = interface.grader_client.grade(
        assignment_id=submission_type,
        user_uuid=request.user.uuid,
        submission_s3_bucket=settings.STORAGE_CLIENT_NAMESPACE,
        submission_s3_key=upload_key,
    )

    application = Application.objects.get(user=request.user)
    Submission.objects.create(
        application=application,
        file_location=upload_key,
        score=submission_result.score,
        feedback_location=submission_result.feedback_s3_key,
        submission_type=submission_type,
    )

    return HttpResponseRedirect(f"/candidate/slu/{submission_type}")


# generic submission views


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

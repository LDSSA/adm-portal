from collections import defaultdict
from typing import Any, Dict

from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import loader
from django.views.decorators.http import require_http_methods

from applications.domain import Domain, Status
from applications.models import Application, Submission, SubmissionTypes
from interface import interface


@require_http_methods(["GET"])
def staff_applications_view(request: HttpRequest) -> HttpResponse:
    query = Application.objects.all().order_by("user__email")

    filter_by_application_status = request.GET.get("application_status")

    applications = []
    count: Dict[Any, int] = defaultdict(int)
    for a in query:
        application_status = Domain.get_application_status(a)
        count[application_status.value] += 1
        if filter_by_application_status is not None and application_status.name != filter_by_application_status:
            continue

        applications.append(
            {
                "ref": a,
                "status_list": [
                    application_status,
                    *[Domain.get_sub_type_status(a, sub_type) for sub_type in SubmissionTypes.all],
                ],
            }
        )

    status_enum = {s.name: {"name": s.name, "value": s.value, "count": count[s.value]} for s in Status}
    ctx = {"status_enum": status_enum, "applications": applications}

    template = loader.get_template("./staff_templates/applications.html")
    return HttpResponse(template.render(ctx, request))


@require_http_methods(["GET"])
def staff_submissions_view(request: HttpRequest) -> HttpResponse:
    query = Submission.objects.all().order_by("-created_at")

    user_email = request.GET.get("user_email", None)
    if user_email is not None:
        query = query.filter(application__user__email__contains=user_email)
    else:
        query = query[:25]

    ctx = {
        "submissions": query.values(
            "id", "application__user__id", "application__user__email", "submission_type", "score"
        )
    }

    template = loader.get_template("./staff_templates/submissions.html")
    return HttpResponse(template.render(ctx, request))


@require_http_methods(["GET"])
def staff_submission_download_view(request: HttpRequest, submission_id: int) -> HttpResponse:
    try:
        submission: Submission = Submission.objects.get(id=submission_id)
    except Submission.DoesNotExist:
        raise Http404

    url = interface.storage_client.get_attachment_url(
        submission.file_location, content_type="application/vnd.jupyter", filename=f"{submission.id}.ipynb"
    )

    return HttpResponseRedirect(url)


@require_http_methods(["GET"])
def staff_submission_feedback_download_view(request: HttpRequest, submission_id: int) -> HttpResponse:
    try:
        submission: Submission = Submission.objects.get(id=submission_id)
    except Submission.DoesNotExist:
        raise Http404
    url = interface.storage_client.get_url(submission.feedback_location, content_type="text/html")

    return HttpResponseRedirect(url)

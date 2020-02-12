from datetime import datetime

from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import loader
from django.views.decorators.http import require_http_methods

from applications.files import get_coding_test_url_from_s3, upload_coding_test_solution
from applications.models import Application, CodingTestSubmission
from interface import get_feature_flag_client, get_grader_client
from profiles.forms import ProfileForm
from profiles.models import Profile
from users.models import to_user_data


@require_http_methods(["GET"])
def candidate_home_view(request: HttpRequest) -> HttpResponse:
    template = loader.get_template("./candidate_templates/home.html")
    application, _ = Application.objects.get_or_create(user=request.user)
    ctx = {"user": request.user, "application": application}
    return HttpResponse(template.render(ctx, request))


def candidate_profile_view(request: HttpRequest) -> HttpResponse:
    profile, created = Profile.objects.get_or_create(user=request.user)

    # if this is a POST request redirect to edit page
    if request.method == "POST":
        return HttpResponseRedirect("/candidate/profile/edit")

    # if this is a GET (or any other method) we'll create a form
    # pre-filled with the current user's profile info
    else:
        if created:
            return HttpResponseRedirect("/candidate/profile/edit")
        form = ProfileForm(instance=profile)

    template = loader.get_template("./candidate_templates/profile.html")
    context = {"form": form}

    return HttpResponse(template.render(context, request))


def candidate_profile_edit(request: HttpRequest) -> HttpResponse:
    profile, _ = Profile.objects.get_or_create(user=request.user)

    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request
        form = ProfileForm(request.POST, instance=profile)

        # check whether it's valid:
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/candidate/profile")

    # if this is a GET (or any other method) we'll create a form
    # pre-filled with the current user's profile info
    else:
        form = ProfileForm(instance=profile)

    template = loader.get_template("./candidate_templates/profile_edit.html")
    context = {"form": form}

    return HttpResponse(template.render(context, request))


def candidate_coding_test_view(request: HttpRequest) -> HttpResponse:
    template = loader.get_template("./candidate_templates/coding_test.html")
    application, _ = Application.objects.get_or_create(user=request.user)
    ctx = {
        "status": application.coding_test_status,
        "submissions_closes_at": application.coding_test_submission_closes_at,
        "passed": application.coding_test_passed,
        "failed": (
            not application.coding_test_passed
            and application.coding_test_downloaded_at is not None
            and not application.coding_test_submission_is_open
        ),
        "best_score": application.coding_test_best_score,
        "download_enabled": True,  # todo use feature flag?
        "upload_enabled": (
            application.coding_test_submission_is_open and get_feature_flag_client().accepting_test_submissions()
        ),
        "submissions": CodingTestSubmission.objects.filter(application=application).order_by("-updated_at"),
    }
    return HttpResponse(template.render(ctx, request))


@require_http_methods(["GET"])
def candidate_coding_test_download_view(request: HttpRequest) -> HttpResponse:
    url = get_coding_test_url_from_s3(settings.STORAGE_CLIENT_NAMESPACE)
    application = Application.objects.get(user=request.user)
    if application.coding_test_downloaded_at is None:
        application.coding_test_downloaded_at = datetime.now()
        application.save()

    return HttpResponseRedirect(url)


@require_http_methods(["POST"])
def candidate_coding_test_upload_view(request: HttpRequest) -> HttpResponse:
    file = request.FILES["file"]

    upload_key = upload_coding_test_solution(to_user_data(request.user), file)

    submission_result = get_grader_client().grade(
        assignment_id="coding_test",
        user_uuid=request.user.uuid,
        submission_s3_bucket=settings.STORAGE_CLIENT_NAMESPACE,
        submission_s3_key=upload_key,
    )

    submission = CodingTestSubmission(
        file_location=upload_key, score=submission_result.score, feedback_location=submission_result.feedback_s3_key
    )
    application = Application.objects.get(user=request.user)
    application.new_coding_test_submission(submission)

    return HttpResponseRedirect("/candidate/coding-test")

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import loader
from django.views.decorators.http import require_http_methods

from applications.models import Application
from profiles.forms import ProfileForm
from profiles.models import Profile


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


def candidate_python_test_view(request: HttpRequest) -> HttpResponse:
    template = loader.get_template("./candidate_templates/python_test.html")
    application, _ = Application.objects.get_or_create(user=request.user)
    ctx = {
        "status": application.python_test_status,
        "passed": application.python_test_passed,
        "failed": (
            not application.python_test_passed
            and application.python_test_downloaded_at is not None
            and not application.python_test_submission_is_open
        ),
    }
    return HttpResponse(template.render(ctx, request))

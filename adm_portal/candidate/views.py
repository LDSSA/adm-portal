from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import loader
from django.views.decorators.http import require_http_methods

from applications.models import Application
from profiles.forms import ProfileForm
from profiles.models import Profile

from .domain import Domain
from .helpers import build_context


@require_http_methods(["GET"])
def candidate_home_view(request: HttpRequest) -> HttpResponse:
    template = loader.get_template("./candidate_templates/home.html")
    application, _ = Application.objects.get_or_create(user=request.user)
    ctx = build_context(request.user, {"user": request.user, "state": Domain.get_candidate_state(request.user)})
    return HttpResponse(template.render(ctx, request))


@require_http_methods(["GET", "POST"])
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
    context = build_context(request.user, {"form": form})

    return HttpResponse(template.render(context, request))


@require_http_methods(["GET", "POST"])
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
    context = build_context(request.user, {"form": form})

    return HttpResponse(template.render(context, request))


@require_http_methods(["GET", "POST"])
def candidate_code_of_conduct_view(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        template = loader.get_template("./candidate_templates/code_of_conduct.html")
        ctx = build_context(request.user, {"code_of_conduct_accepted": request.user.code_of_conduct_accepted})
        return HttpResponse(template.render(ctx, request))

    request.user.code_of_conduct_accepted = True
    request.user.save()

    return HttpResponseRedirect("/candidate/code-of-conduct")

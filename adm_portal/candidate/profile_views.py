from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import loader
from django.views.decorators.http import require_http_methods

from profiles.models import Profile

from .helpers import build_context


def _get_candidate_profile_view(request: HttpRequest, profile: Profile) -> HttpResponse:
    template = loader.get_template("./candidate_templates/profile.html")
    context = build_context(request.user, {"profile": profile, "profile_exists": profile.id is not None})

    return HttpResponse(template.render(context, request))


def _post_candidate_profile_view(request: HttpRequest, profile: Profile) -> HttpResponse:
    profile.full_name = request.POST["full_name"]
    profile.profession = request.POST["profession"]
    profile.gender = request.POST["gender"]
    profile.ticket_type = request.POST["ticket_type"]
    profile.save()

    return HttpResponseRedirect("/candidate/home")


@require_http_methods(["GET", "POST"])
def candidate_profile_view(request: HttpRequest) -> HttpResponse:
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile = Profile(user=request.user)

    if request.method == "GET":
        return _get_candidate_profile_view(request, profile)
    return _post_candidate_profile_view(request, profile)

    # try:
    #     profile = Profile.objects.get(user=request.user)
    # except Profile.DoesNotExist:
    #     profile = Profile()
    #
    # # if this is a POST request redirect to edit page
    # if request.method == "POST":
    #     return HttpResponseRedirect("/candidate/profile/edit")
    #
    # # if this is a GET (or any other method) we'll create a form
    # # pre-filled with the current user's profile info
    # else:
    #     if created:
    #         return HttpResponseRedirect("/candidate/profile/edit")
    #     form = ProfileForm(instance=profile)
    #
    # template = loader.get_template("./candidate_templates/profile.html")
    # context = build_context(request.user, {"form": form})
    #
    # return HttpResponse(template.render(context, request))

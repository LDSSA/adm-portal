from typing import Optional

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import loader
from django.views.decorators.http import require_http_methods

from profiles.models import Profile, ProfileGenders, ProfileTicketTypes

from .helpers import build_context


def _get_candidate_profile_view(request: HttpRequest, profile: Optional[Profile]) -> HttpResponse:
    template = loader.get_template("./candidate_templates/profile.html")
    context = build_context(
        request.user,
        {
            "profile": profile,
            "profile_exists": profile is not None,
            "profile_genders": ProfileGenders,
            "profile_ticket_types": ProfileTicketTypes,
            "applying_for_scholarship": request.user.applying_for_scholarship,
        },
    )

    return HttpResponse(template.render(context, request))


def _post_candidate_profile_view(request: HttpRequest, profile: Optional[Profile]) -> HttpResponse:
    if profile is None:
        profile = Profile(user=request.user)
    profile.full_name = request.POST["full_name"]
    profile.profession = request.POST["profession"]
    profile.gender = request.POST["gender"]
    profile.ticket_type = (
        request.POST["ticket_type"]
        if request.user.applying_for_scholarship is False
        else ProfileTicketTypes.scholarship
    )
    profile.company = request.POST["company"] if request.user.applying_for_scholarship is False else ""

    profile.save()
    return HttpResponseRedirect("/candidate/home")


@require_http_methods(["GET", "POST"])
def candidate_profile_view(request: HttpRequest) -> HttpResponse:
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile = None

    if request.method == "GET":
        return _get_candidate_profile_view(request, profile)
    return _post_candidate_profile_view(request, profile)

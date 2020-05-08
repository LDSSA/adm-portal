from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import loader
from django.views.decorators.http import require_http_methods

from applications.models import Application

from .domain import Domain
from .helpers import build_context


@require_http_methods(["GET"])
def candidate_home_view(request: HttpRequest) -> HttpResponse:
    template = loader.get_template("./candidate_templates/home.html")
    application, _ = Application.objects.get_or_create(user=request.user)
    ctx = build_context(request.user, {"user": request.user, "state": Domain.get_candidate_state(request.user)})
    return HttpResponse(template.render(ctx, request))


@require_http_methods(["GET", "POST"])
def candidate_code_of_conduct_view(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        template = loader.get_template("./candidate_templates/code_of_conduct.html")
        ctx = build_context(request.user, {"code_of_conduct_accepted": request.user.code_of_conduct_accepted})
        return HttpResponse(template.render(ctx, request))

    request.user.code_of_conduct_accepted = True
    request.user.save()

    return HttpResponseRedirect("/candidate/home")

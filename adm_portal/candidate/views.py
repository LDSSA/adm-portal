from django.http import HttpRequest, HttpResponse
from django.template import loader
from django.views.decorators.http import require_http_methods

from applications.models import Application


@require_http_methods(["GET"])
def candidate_home_view(request: HttpRequest) -> HttpResponse:
    template = loader.get_template("./home.html")
    application, _ = Application.objects.get_or_create(user=request.user)
    ctx = {"user": request.user, "application": application}
    return HttpResponse(template.render(ctx, request))

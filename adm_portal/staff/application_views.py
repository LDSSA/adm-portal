from django.http import HttpRequest, HttpResponse
from django.template import loader
from django.views.decorators.http import require_http_methods

from applications.models import Application


@require_http_methods(["GET"])
def staff_applications_view(request: HttpRequest) -> HttpResponse:
    # todo: fix this
    ctx = {"applications": Application.objects.all().order_by("user__email")}
    template = loader.get_template("./staff_templates/applications.html")
    return HttpResponse(template.render(ctx, request))

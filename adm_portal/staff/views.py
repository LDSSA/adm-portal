from django.http import HttpRequest, HttpResponse
from django.template import loader
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def staff_home_view(request: HttpRequest) -> HttpResponse:
    template = loader.get_template("./staff_templates/home.html")
    ctx = {"user": request.user}
    return HttpResponse(template.render(ctx, request))

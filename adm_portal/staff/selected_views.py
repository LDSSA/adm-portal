from django.http import HttpRequest, HttpResponse
from django.template import loader
from django.views.decorators.http import require_http_methods

from selected.models import Selected


@require_http_methods(["GET"])
def staff_selected_candidates_view(request: HttpRequest) -> HttpResponse:
    ctx = {"selected_candidates": Selected.objects.all()}
    template = loader.get_template("./staff_templates/selected.html")
    return HttpResponse(template.render(ctx, request))

from django.http import HttpRequest, HttpResponse
from django.template import loader
from django.views.decorators.http import require_http_methods

from profiles.models import Profile


@require_http_methods(["GET"])
def staff_profiles_view(request: HttpRequest) -> HttpResponse:
    ctx = {"profiles": Profile.objects.all().order_by("user__email")}
    template = loader.get_template("./staff_templates/profiles.html")
    return HttpResponse(template.render(ctx, request))

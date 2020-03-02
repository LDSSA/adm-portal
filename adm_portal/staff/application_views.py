from django.http import HttpRequest, HttpResponse
from django.template import loader
from django.views.decorators.http import require_http_methods

from applications.domain import Domain
from applications.models import Application, SubmissionTypes


@require_http_methods(["GET"])
def staff_applications_view(request: HttpRequest) -> HttpResponse:
    # todo: fix this
    ctx = {
        "applications": [
            {
                "ref": a,
                "status_list": [
                    Domain.get_application_status(a),
                    *[Domain.get_sub_type_status(a, sub_type) for sub_type in SubmissionTypes.all],
                ],
            }
            for a in Application.objects.all().order_by("user__email")
        ]
    }

    template = loader.get_template("./staff_templates/applications.html")
    return HttpResponse(template.render(ctx, request))

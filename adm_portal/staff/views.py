from logging import getLogger

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import loader
from django.views.decorators.http import require_http_methods

from interface import interface

logger = getLogger(__name__)


def _get_staff_home_view(request: HttpRequest) -> HttpResponse:
    template = loader.get_template("./staff_templates/home.html")
    ctx = {
        "user": request.user,
        "flags": [
            {"key": "signups_are_open", "value": interface.feature_flag_client.signups_are_open(), "label": "Signups"},
            {
                "key": "applications_are_open",
                "value": interface.feature_flag_client.applications_are_open(),
                "label": "Challenge Submissions",
            },
            {
                "key": "accepting_payment_profs",
                "value": interface.feature_flag_client.accepting_payment_profs(),
                "label": "Payment Proof Uploads",
            },
        ],
    }
    return HttpResponse(template.render(ctx, request))


def _post_staff_home_view(request: HttpRequest) -> HttpResponse:
    action = request.POST["action"]
    key = request.POST["key"]

    if key == "signups_are_open":
        if action == "open":
            interface.feature_flag_client.open_signups()
        else:
            interface.feature_flag_client.close_signups()
    elif key == "applications_are_open":
        if action == "open":
            interface.feature_flag_client.open_applications()
        else:
            interface.feature_flag_client.close_applications()
    elif key == "accepting_payment_profs":
        if action == "open":
            interface.feature_flag_client.open_payment_profs()
        else:
            interface.feature_flag_client.close_payment_profs()
    else:
        logger.warning(f"unknown feature flag key `{key}`.. doing nothing")

    return HttpResponseRedirect("/staff/home")


@require_http_methods(["GET", "POST"])
def staff_home_view(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        return _get_staff_home_view(request)
    return _post_staff_home_view(request)

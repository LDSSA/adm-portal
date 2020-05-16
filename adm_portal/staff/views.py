from datetime import datetime
from logging import getLogger

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.template import loader
from django.views.decorators.http import require_http_methods

from interface import interface

logger = getLogger(__name__)


DATETIME_FMT = "%d/%m/%Y %H:%M:%S"


def _get_staff_home_view(request: HttpRequest) -> HttpResponse:
    template = loader.get_template("./staff_templates/home.html")

    ctx = {
        "user": request.user,
        "datetime_fmt": DATETIME_FMT,
        "datetime_flags": [
            {
                "key": "applications_opening_date",
                "value": interface.feature_flag_client.get_applications_opening_date().strftime(DATETIME_FMT),
                "label": "Challenge Submissions Opening Date",
            },
            {
                "key": "applications_closing_date",
                "value": interface.feature_flag_client.get_applications_closing_date().strftime(DATETIME_FMT),
                "label": "Challenge Submissions Closing Date",
            },
        ],
        "int_flags": [
            {
                "key": "coding_test_duration",
                "value": interface.feature_flag_client.get_coding_test_duration(),
                "label": "Coding Test Duration in minutes",
            }
        ],
        "bool_flags": [
            {"key": "signups_are_open", "value": interface.feature_flag_client.signups_are_open(), "label": "Signups"},
            {
                "key": "accepting_payment_profs",
                "value": interface.feature_flag_client.accepting_payment_profs(),
                "label": "Payment Proof Uploads",
            },
        ],
    }
    return HttpResponse(template.render(ctx, request))


def _post_staff_home_view(request: HttpRequest) -> HttpResponse:
    if not request.user.is_admin:
        return HttpResponseServerError(b"error updating admin variables. Only admins can update these variables")

    key = request.POST["key"]

    if key == "applications_opening_date":
        date_s = request.POST["date_s"]
        if not interface.feature_flag_client.set_applications_opening_date(datetime.strptime(date_s, DATETIME_FMT)):
            return HttpResponseServerError(b"error setting opening date. opening date must be before closing date")

    elif key == "applications_closing_date":
        date_s = request.POST["date_s"]
        if not interface.feature_flag_client.set_applications_closing_date(datetime.strptime(date_s, DATETIME_FMT)):
            return HttpResponseServerError(b"error setting closing date. closing date must be after opening date")

    elif key == "coding_test_duration":
        interface.feature_flag_client.set_coding_test_duration(int(request.POST["int_s"]))

    elif key == "signups_are_open":
        if request.POST["action"] == "open":
            interface.feature_flag_client.open_signups()
        else:
            interface.feature_flag_client.close_signups()

    elif key == "accepting_payment_profs":
        if request.POST["action"] == "open":
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

from logging import getLogger

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.template import loader
from django.views.decorators.http import require_http_methods

from .domain import Events, EventsException

logger = getLogger(__name__)


def _get_staff_events_view(request: HttpRequest) -> HttpResponse:
    template = loader.get_template("./staff_templates/events.html")

    ctx = {
        "user": request.user,
        "emails": [
            {
                "key": "applications_over",
                "sent_to": Events.applications_are_over_sent_emails(),
                "applicable_to": Events.applications_are_over_total_emails(),
                "label": "End Applications",
            },
            {
                "key": "admissions_over",
                "sent_to": Events.admissions_are_over_sent_emails(),
                "applicable_to": Events.admissions_are_over_total_emails(),
                "label": "End Admissions",
            },
        ],
    }
    return HttpResponse(template.render(ctx, request))


def _post_staff_events_view(request: HttpRequest) -> HttpResponse:
    if not request.user.is_admin:
        return HttpResponseServerError(b"error triggering event. Only admins can trigger events")

    key = request.POST["key"]

    if key == "applications_over":
        try:
            Events.trigger_applications_are_over()
        except EventsException:
            return HttpResponseServerError(b"error triggering event. Are you sure applications are over?")

    elif key == "admissions_over":
        try:
            Events.trigger_admissions_are_over()
        except EventsException:
            return HttpResponseServerError(
                b"error triggering event. Make sure there are no candidates in `drawn` or `selected`"
            )

    return HttpResponseRedirect("/staff/events")


@require_http_methods(["GET", "POST"])
def staff_events_view(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        return _get_staff_events_view(request)
    return _post_staff_events_view(request)

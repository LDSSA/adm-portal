from typing import Any, Dict, List

from django.http import HttpRequest, HttpResponse
from django.template import loader

from .models import Profile


def profiles_view(request: HttpRequest) -> HttpResponse:
    context = get_context()
    template = loader.get_template(_TEMPLATE_NAME)

    return HttpResponse(template.render(context, request))


def get_context() -> Dict[str, Any]:
    profiles = list(Profile.objects.all().values())

    return {"column_names": _COL_NAMES, "profiles": profiles}


_COL_NAMES: List[str] = [
    "ID",  # todo: fix me, probably show user email
    "Full Name",
    "Profession",
    "Gender",
    "Ticket Type",
    "Updated At",
    "Created At",
]

_TEMPLATE_NAME = "./table.html"

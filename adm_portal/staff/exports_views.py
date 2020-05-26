from datetime import datetime

from django.http import HttpRequest, HttpResponse
from django.template import loader
from django.views.decorators.http import require_http_methods

from common.export import csv_export_view

from .export import get_all_candidates


@require_http_methods(["GET"])
def staff_exports_view(request: HttpRequest) -> HttpResponse:
    template = loader.get_template("./staff_templates/exports.html")

    return HttpResponse(template.render({}, request))


@require_http_methods(["GET"])
def export_candidates_view(request: HttpRequest) -> HttpResponse:
    export_data = get_all_candidates()
    return csv_export_view(export_data, filename=f"candidates@{datetime.now().strftime('%Y-%m-%d_%H:%M')}.csv")

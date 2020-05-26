import csv
from typing import Any, Dict, List, NamedTuple

from django.http import HttpResponse


class ExportData(NamedTuple):
    headers: List[str]
    rows: List[Dict[str, Any]]


def csv_export_view(data: ExportData, filename: str) -> HttpResponse:

    response = HttpResponse(status=200, content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'

    w = csv.DictWriter(response, data.headers, lineterminator="\n")
    w.writeheader()
    w.writerows(data.rows)

    return response

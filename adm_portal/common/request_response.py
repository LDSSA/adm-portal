from django.http import HttpRequest


def get_url(request: HttpRequest) -> str:
    scheme = "https" if request.is_secure() else "http"
    host = request.get_host()
    return f"{scheme}://{host}"

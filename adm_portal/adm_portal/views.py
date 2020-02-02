from django.http import HttpRequest, HttpResponse


def ping_pong() -> str:
    return "Pong"


def ping_view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("<html><body>Pong</body></html>")


def hello_view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("<html><body>Hello World!</body></html>")

from django.http import HttpRequest, HttpResponse
from django.template import loader

from interface import get_storage_client

from .models import Profile


# old example of rendering all the profiles
def profiles_view(request: HttpRequest) -> HttpResponse:
    column_names = [
        "ID",  # todo: fix me, probably show user email
        "Full Name",
        "Profession",
        "Gender",
        "Ticket Type",
        "Updated At",
        "Created At",
    ]

    context = {"column_names": column_names, "profiles": list(Profile.objects.all().values())}

    template = loader.get_template("./table.html")

    return HttpResponse(template.render(context, request))


# this is just an example for the view to come
# to consider: auth, file size, how to build key (use user id or something like that)
def upload_file_view(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        template = loader.get_template("./home.html")
        return HttpResponse(template.render({}, request))

    file = request.FILES["file"]

    get_storage_client().save(file.name, file)
    return HttpResponse("Success")

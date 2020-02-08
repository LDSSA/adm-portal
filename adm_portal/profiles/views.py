from django.http import HttpRequest, HttpResponse
from django.template import loader

from interface import get_storage_client

from .forms import ProfileForm
from .models import Profile


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


def profile_view(request: HttpRequest) -> HttpResponse:
    profile, _ = Profile.objects.get_or_create(user=request.user)

    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request
        form = ProfileForm(request.POST, instance=profile)

        # check whether it's valid:
        if form.is_valid():
            form.save()
            return HttpResponse("Profile updated!")

    # if this is a GET (or any other method) we'll create a form
    # pre-filled with the current user's profile info
    else:
        form = ProfileForm(instance=profile)

    template = loader.get_template("./profile.html")
    context = {"form": form}

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

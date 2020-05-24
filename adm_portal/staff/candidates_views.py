from typing import Optional

from django.http import Http404, HttpRequest, HttpResponse
from django.template import loader
from django.views.decorators.http import require_http_methods

from applications.domain import Domain as ApplicationDomain
from applications.models import Application, Submission, SubmissionTypes
from interface import interface
from profiles.models import Profile
from users.models import User


@require_http_methods(["GET"])
def staff_candidate_view(request: HttpRequest, user_id: int) -> HttpResponse:
    try:
        user = User.objects.filter(is_staff=False).filter(is_admin=False).get(id=user_id)
    except User.DoesNotExist:
        raise Http404

    id_card_url: Optional[str] = None
    try:
        id_card_url = (
            interface.storage_client.get_url(user.profile.id_card_location, content_type="image")
            if user.profile.id_card_location is not None
            else None
        )
    except Profile.DoesNotExist:
        pass

    try:
        application = user.application
        total_submissions = Submission.objects.filter(application=application).count()
        application_best_scores = {
            SubmissionTypes.coding_test.uname: ApplicationDomain.get_best_score(
                application, SubmissionTypes.coding_test
            ),
            SubmissionTypes.slu01.uname: ApplicationDomain.get_best_score(application, SubmissionTypes.slu01),
            SubmissionTypes.slu02.uname: ApplicationDomain.get_best_score(application, SubmissionTypes.slu02),
            SubmissionTypes.slu03.uname: ApplicationDomain.get_best_score(application, SubmissionTypes.slu03),
        }
    except Application.DoesNotExist:
        total_submissions = 0
        application_best_scores = {}

    ctx = {
        "user": user,
        "total_submissions": total_submissions,
        "application_best_scores": application_best_scores,
        "id_card_url": id_card_url,
    }
    template = loader.get_template("./staff_templates/candidate.html")
    return HttpResponse(template.render(ctx, request))


@require_http_methods(["GET"])
def staff_candidates_view(request: HttpRequest) -> HttpResponse:
    ctx = {"users": User.objects.filter(is_staff=False).filter(is_admin=False).order_by("email")}
    template = loader.get_template("./staff_templates/candidates.html")
    return HttpResponse(template.render(ctx, request))

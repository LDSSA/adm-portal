from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import loader
from django.views.decorators.http import require_http_methods

from selected.domain import Domain, DomainQueries
from selected.models import PassedCandidate


@require_http_methods(["GET"])
def staff_selected_candidates_view(request: HttpRequest) -> HttpResponse:
    passed_test = DomainQueries.get_passed_test()
    drawn = DomainQueries.get_drawn()
    selected_accepted = DomainQueries.get_selected_accepted()

    drawn_candidates = drawn.count()
    drawn_female = drawn.filter(user__profile__gender="f").count()
    drawn_company = drawn.filter(user__profile__ticket_type="company").count()

    selected_accepted_candidates = selected_accepted.count()
    selected_accepted_female = selected_accepted.filter(user__profile__gender="f").count()
    selected_accepted_company = selected_accepted.filter(user__profile__ticket_type="company").count()

    left_out_candidates = passed_test.count()
    left_out_females = passed_test.filter(user__profile__gender="f").count()
    left_out_non_company = passed_test.filter(user__profile__ticket_type="company").count()

    ctx = {
        "first_table_candidates": selected_accepted,
        "second_table_candidates": drawn,
        "summary": {
            "drawn_candidates": drawn_candidates,
            "drawn_female": drawn_female,
            "drawn_company": drawn_company,
            "selected_accepted_candidates": selected_accepted_candidates,
            "selected_accepted_female": selected_accepted_female,
            "selected_accepted_company": selected_accepted_company,
            "total_candidates": drawn_candidates + selected_accepted_candidates,
            "total_female": drawn_female + selected_accepted_female,
            "total_company": drawn_company + selected_accepted_company,
            # TODO: Go get the 50 to the DrawParams
            "pct_candidates": (drawn_candidates + selected_accepted_candidates) / 50 * 100,
            "pct_female": (drawn_female + selected_accepted_female) / 50 * 100,
            "pct_company": (drawn_company + selected_accepted_company) / 50 * 100,
            "left_out_candidates": left_out_candidates,
            "left_out_females": left_out_females,
            "left_out_non_company": left_out_non_company,
        },
    }
    template = loader.get_template("./staff_templates/selected.html")
    return HttpResponse(template.render(ctx, request))


@require_http_methods(["POST"])
def staff_draw_candidates_view(request: HttpRequest) -> HttpResponseRedirect:
    Domain.make_draw()

    return HttpResponseRedirect("/staff/selected-candidates/")


@require_http_methods(["POST"])
def staff_select_candidates_view(request: HttpRequest) -> HttpResponseRedirect:
    Domain.select()

    return HttpResponseRedirect("/staff/selected-candidates/")


@require_http_methods(["POST"])
def staff_reject_candidate_view(request: HttpRequest, candidate_id: int) -> HttpResponseRedirect:
    candidate = PassedCandidate.objects.get(id=candidate_id)
    Domain.reject_draw(candidate)

    return HttpResponseRedirect("/staff/selected-candidates/")

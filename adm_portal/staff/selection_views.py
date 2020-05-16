from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import loader
from django.views.decorators.http import require_http_methods

from selection.draw import default_draw_params, draw, reject_draw
from selection.models import Selection
from selection.queries import SelectionQueries
from selection.select import select
from selection.status import SelectionStatus


@require_http_methods(["GET"])
def staff_selection_candidates_view(request: HttpRequest) -> HttpResponse:
    passed_test = SelectionQueries.filter_by_status_in([SelectionStatus.PASSED_TEST])
    drawn = SelectionQueries.filter_by_status_in([SelectionStatus.DRAWN])
    after_draw = SelectionQueries.filter_by_status_in(
        [SelectionStatus.INTERVIEW, SelectionStatus.SELECTED, SelectionStatus.TO_BE_ACCEPTED, SelectionStatus.ACCEPTED]
    )

    drawn_candidates = drawn.count()
    drawn_female = drawn.filter(user__profile__gender="f").count()
    drawn_company = drawn.filter(user__profile__ticket_type="company").count()

    selected_accepted_candidates = after_draw.count()
    selected_accepted_female = after_draw.filter(user__profile__gender="f").count()
    selected_accepted_company = after_draw.filter(user__profile__ticket_type="company").count()

    left_out_candidates = passed_test.count()
    left_out_females = passed_test.filter(user__profile__gender="f").count()
    left_out_non_company = passed_test.filter(user__profile__ticket_type="company").count()

    ctx = {
        "first_table_candidates": after_draw,
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
            "pct_candidates": (drawn_candidates + selected_accepted_candidates)
            / default_draw_params.number_of_seats
            * 100,
            "pct_female": (drawn_female + selected_accepted_female) / default_draw_params.number_of_seats * 100,
            "pct_company": (drawn_company + selected_accepted_company) / default_draw_params.number_of_seats * 100,
            "left_out_candidates": left_out_candidates,
            "left_out_females": left_out_females,
            "left_out_non_company": left_out_non_company,
        },
    }
    template = loader.get_template("./staff_templates/selected.html")
    return HttpResponse(template.render(ctx, request))


@require_http_methods(["POST"])
def staff_draw_candidates_view(request: HttpRequest) -> HttpResponseRedirect:
    draw(default_draw_params)
    return HttpResponseRedirect("/staff/selections/")


@require_http_methods(["POST"])
def staff_reject_selection_view(request: HttpRequest, candidate_id: int) -> HttpResponseRedirect:
    selection = Selection.objects.get(id=candidate_id)
    reject_draw(selection)

    return HttpResponseRedirect("/staff/selections/")


@require_http_methods(["POST"])
def staff_select_candidates_view(request: HttpRequest) -> HttpResponseRedirect:
    select()
    return HttpResponseRedirect("/staff/selections/")

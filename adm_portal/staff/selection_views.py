from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import loader
from django.views.decorators.http import require_http_methods

from profiles.models import ProfileGenders, ProfileTicketTypes
from selection.draw import default_draw_params, draw, reject_draw
from selection.models import Selection
from selection.queries import SelectionQueries
from selection.select import select
from selection.status import SelectionStatus


@require_http_methods(["GET"])
def staff_selection_candidates_view(request: HttpRequest) -> HttpResponse:
    all_passed_test = SelectionQueries.filter_by_status_in([SelectionStatus.PASSED_TEST])
    all_drawn = SelectionQueries.filter_by_status_in([SelectionStatus.DRAWN])
    all_after_draw = SelectionQueries.filter_by_status_in(
        [SelectionStatus.INTERVIEW, SelectionStatus.SELECTED, SelectionStatus.TO_BE_ACCEPTED, SelectionStatus.ACCEPTED]
    )

    # no scholarships
    passed_test_no_scholarships = SelectionQueries.no_scholarships(all_passed_test)
    drawn_no_scholarships = SelectionQueries.no_scholarships(all_drawn)
    after_draw_no_scholarships = SelectionQueries.no_scholarships(all_after_draw)

    drawn_candidates_no_scholarships = drawn_no_scholarships.count()
    drawn_female_no_scholarships = drawn_no_scholarships.filter(user__profile__gender=ProfileGenders.female).count()
    drawn_company_no_scholarships = drawn_no_scholarships.filter(
        user__profile__ticket_type=ProfileTicketTypes.company
    ).count()

    selected_accepted_candidates_no_scholarships = after_draw_no_scholarships.count()
    selected_accepted_female_no_scholarships = after_draw_no_scholarships.filter(
        user__profile__gender=ProfileGenders.female
    ).count()
    selected_accepted_company_no_scholarships = after_draw_no_scholarships.filter(
        user__profile__ticket_type=ProfileTicketTypes.company
    ).count()

    left_out_candidates_no_scholarships = passed_test_no_scholarships.count()
    left_out_females_no_scholarships = passed_test_no_scholarships.filter(
        user__profile__gender=ProfileGenders.female
    ).count()
    left_out_non_company_no_scholarships = passed_test_no_scholarships.filter(
        user__profile__ticket_type=ProfileTicketTypes.company
    ).count()

    # scholarships
    passed_test_scholarships = SelectionQueries.scholarships(all_passed_test)
    drawn_scholarships = SelectionQueries.scholarships(all_drawn)
    after_draw_scholarships = SelectionQueries.scholarships(all_after_draw)

    drawn_candidates_scholarships = drawn_scholarships.count()
    drawn_female_scholarships = drawn_scholarships.filter(user__profile__gender=ProfileGenders.female).count()
    drawn_company_scholarships = drawn_scholarships.filter(
        user__profile__ticket_type=ProfileTicketTypes.company
    ).count()

    selected_accepted_candidates_scholarships = after_draw_scholarships.count()
    selected_accepted_female_scholarships = after_draw_scholarships.filter(
        user__profile__gender=ProfileGenders.female
    ).count()
    selected_accepted_company_scholarships = after_draw_scholarships.filter(
        user__profile__ticket_type=ProfileTicketTypes.company
    ).count()

    left_out_candidates_scholarships = passed_test_scholarships.count()
    left_out_females_scholarships = passed_test_scholarships.filter(
        user__profile__gender=ProfileGenders.female
    ).count()
    left_out_non_company_scholarships = passed_test_scholarships.filter(
        user__profile__ticket_type=ProfileTicketTypes.company
    ).count()

    ctx = {
        "first_table_candidates": all_after_draw,
        "second_table_candidates": all_drawn,
        "summary": {
            "no_scholarship": {
                "drawn_candidates": drawn_candidates_no_scholarships,
                "drawn_female": drawn_female_no_scholarships,
                "drawn_company": drawn_company_no_scholarships,
                "selected_accepted_candidates": selected_accepted_candidates_no_scholarships,
                "selected_accepted_female": selected_accepted_female_no_scholarships,
                "selected_accepted_company": selected_accepted_company_no_scholarships,
                "total_candidates": drawn_candidates_no_scholarships + selected_accepted_candidates_no_scholarships,
                "total_female": drawn_female_no_scholarships + selected_accepted_female_no_scholarships,
                "total_company": drawn_company_no_scholarships + selected_accepted_company_no_scholarships,
                "pct_candidates": (drawn_candidates_no_scholarships + selected_accepted_candidates_no_scholarships)
                / default_draw_params.number_of_seats
                * 100,
                "pct_female": (drawn_female_no_scholarships + selected_accepted_female_no_scholarships)
                / default_draw_params.number_of_seats
                * 100,
                "pct_company": (drawn_company_no_scholarships + selected_accepted_company_no_scholarships)
                / default_draw_params.number_of_seats
                * 100,
                "left_out_candidates": left_out_candidates_no_scholarships,
                "left_out_females": left_out_females_no_scholarships,
                "left_out_non_company": left_out_non_company_no_scholarships,
            },
            "scholarship": {
                "drawn_candidates": drawn_candidates_scholarships,
                "drawn_female": drawn_female_scholarships,
                "drawn_company": drawn_company_scholarships,
                "selected_accepted_candidates": selected_accepted_candidates_scholarships,
                "selected_accepted_female": selected_accepted_female_scholarships,
                "selected_accepted_company": selected_accepted_company_scholarships,
                "total_candidates": drawn_candidates_scholarships + selected_accepted_candidates_scholarships,
                "total_female": drawn_female_scholarships + selected_accepted_female_scholarships,
                "total_company": drawn_company_scholarships + selected_accepted_company_scholarships,
                "pct_candidates": (drawn_candidates_scholarships + selected_accepted_candidates_scholarships)
                / default_draw_params.number_of_seats
                * 100,
                "pct_female": (drawn_female_scholarships + selected_accepted_female_scholarships)
                / default_draw_params.number_of_seats
                * 100,
                "pct_company": (drawn_company_scholarships + selected_accepted_company_scholarships)
                / default_draw_params.number_of_seats
                * 100,
                "left_out_candidates": left_out_candidates_scholarships,
                "left_out_females": left_out_females_scholarships,
                "left_out_non_company": left_out_non_company_scholarships,
            },
        },
    }
    template = loader.get_template("./staff_templates/selections.html")
    return HttpResponse(template.render(ctx, request))


@require_http_methods(["POST"])
def staff_draw_candidates_view(request: HttpRequest) -> HttpResponseRedirect:
    draw(default_draw_params, scholarships=False)
    draw(default_draw_params, scholarships=True)
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

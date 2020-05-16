from logging import getLogger
from typing import Iterable, List, NamedTuple, Optional

from .domain import SelectionDomain
from .models import Selection
from .queries import SelectionQueries
from .status import SelectionStatus

logger = getLogger(__name__)


class DrawException(Exception):
    pass


class DrawParams(NamedTuple):
    # number of desired "currently" selected
    number_of_seats: int
    min_female_quota: float
    max_company_quota: float


default_draw_params = DrawParams(number_of_seats=50, min_female_quota=0.35, max_company_quota=0.2)


class DrawCounters:
    def __init__(self) -> None:
        self.total = 0
        self.female = 0
        self.company = 0

    def update(self, selection: Selection) -> None:
        profile = selection.user.profile

        self.total += 1

        if profile.gender == "f":
            self.female += 1

        if profile.ticket_type == "company":
            self.company += 1


def must_pick_female(params: DrawParams, counters: DrawCounters) -> bool:
    female_fraction_if_non_female_drawn = counters.female / (counters.total + 1)
    return female_fraction_if_non_female_drawn < params.min_female_quota


def must_not_pick_company(params: DrawParams, counters: DrawCounters) -> bool:
    company_fraction_if_company_drawn = (counters.company + 1) / (counters.total + 1)
    return company_fraction_if_company_drawn >= params.max_company_quota


def get_draw_counters(candidates: Iterable[Selection]) -> DrawCounters:
    counters = DrawCounters()

    for candidate in candidates:
        counters.update(candidate)

    return counters


def draw_next(forbidden_genders: List[str], forbidden_ticket_types: List[str]) -> Optional[Selection]:
    return SelectionQueries.random(SelectionQueries.draw_filter(forbidden_genders, forbidden_ticket_types))


def draw(params: DrawParams) -> None:
    current_candidates = SelectionQueries.filter_by_status_in(
        [
            SelectionStatus.DRAWN,
            SelectionStatus.INTERVIEW,
            SelectionStatus.SELECTED,
            SelectionStatus.TO_BE_ACCEPTED,
            SelectionStatus.ACCEPTED,
        ]
    )
    counters = get_draw_counters(current_candidates)
    draw_rank = SelectionQueries.max_rank(current_candidates) + 1

    while counters.total != params.number_of_seats:
        forbidden_genders = ["m", "other"] if must_pick_female(params, counters) else []
        forbidden_ticket_types = ["company"] if must_not_pick_company(params, counters) else []

        candidate = draw_next(forbidden_genders, forbidden_ticket_types)
        if candidate is None:
            candidate = draw_next([], forbidden_ticket_types)
        if candidate is None:
            candidate = draw_next(forbidden_genders, [])
        if candidate is None:
            candidate = draw_next([], [])
        if candidate is None:
            # no more suitable candidates
            break

        SelectionDomain.update_status(candidate, SelectionStatus.DRAWN, draw_rank=draw_rank)
        counters.update(candidate)
        draw_rank += 1


def reject_draw(selection: Selection) -> None:
    current_status = SelectionDomain.get_status(selection)
    if current_status != SelectionStatus.DRAWN:
        raise DrawException(f"Can't reject draw for candidate in status {current_status}.")

    SelectionDomain.update_status(selection, SelectionStatus.PASSED_TEST)

from logging import getLogger
from typing import Any, List, NamedTuple, Optional

from django.db.models import Max, QuerySet

from selected.models import PassedCandidate, PassedCandidateStatus
from users.models import User

logger = getLogger(__name__)


class DomainException(Exception):
    pass


class DrawParams(NamedTuple):
    # number of desired "currently" selected
    number_of_seats: int
    min_female_quota: float
    max_company_quota: float


class DrawCounters:
    def __init__(self) -> None:
        self.total = 0
        self.female = 0
        self.company = 0

    def update(self, candidate: PassedCandidate) -> None:
        profile = candidate.user.profile

        self.total += 1

        if profile.gender == "f":
            self.female += 1

        if profile.ticket_type == "company":
            self.company += 1


class Domain:
    @staticmethod
    def new_candidate(user: User) -> PassedCandidate:
        candidate, _ = PassedCandidate.objects.get_or_create(user=user)
        return candidate

    @staticmethod
    def must_pick_female(params: DrawParams, counters: DrawCounters) -> bool:
        female_fraction_if_non_female_drawn = counters.female / (counters.total + 1)
        return female_fraction_if_non_female_drawn < params.min_female_quota

    @staticmethod
    def must_not_pick_company(params: DrawParams, counters: DrawCounters) -> bool:
        company_fraction_if_company_drawn = (counters.company + 1) / (counters.total + 1)
        return company_fraction_if_company_drawn >= params.max_company_quota

    @staticmethod
    def get_draw_counters(candidates: List[PassedCandidate]) -> DrawCounters:
        counters = DrawCounters()

        for candidate in candidates:
            counters.update(candidate)

        return counters

    @staticmethod
    def draw_next(forbidden_genders: List[str], forbidden_ticket_types: List[str]) -> Optional[PassedCandidate]:
        try:
            return (
                PassedCandidate.objects.filter(status="passed_test")
                .exclude(user__profile__gender__in=forbidden_genders)
                .exclude(user__profile__ticket_type__in=forbidden_ticket_types)
                .order_by("?")
                .first()
            )
        except PassedCandidate.DoesNotExist:
            return None

    @staticmethod
    def draw(params: DrawParams) -> None:
        current_candidates = DomainQueries.get_drawn_selected_accepted()
        counters = Domain.get_draw_counters(current_candidates)
        draw_rank = DomainQueries.get_max_rank(current_candidates) + 1

        while counters.total != params.number_of_seats:
            forbidden_genders = ["m", "other"] if Domain.must_pick_female(params, counters) else []
            forbidden_ticket_types = ["company"] if Domain.must_not_pick_company(params, counters) else []

            candidate = Domain.draw_next(forbidden_genders, forbidden_ticket_types)
            if candidate is None:
                candidate = Domain.draw_next([], forbidden_ticket_types)
            if candidate is None:
                candidate = Domain.draw_next(forbidden_genders, [])
            if candidate is None:
                candidate = Domain.draw_next([], [])
            if candidate is None:
                # no more suitable candidates
                break

            Domain.update_status(candidate, PassedCandidateStatus.drawn, draw_rank=draw_rank)
            counters.update(candidate)
            draw_rank += 1

    @staticmethod
    def make_draw() -> None:
        Domain.draw(DrawParams(number_of_seats=50, min_female_quota=0.35, max_company_quota=0.2))

    @staticmethod
    def update_status(candidate: PassedCandidate, status: str, *, draw_rank: Optional[int] = None) -> None:
        candidate.status = status

        if draw_rank is not None:
            candidate.draw_rank = draw_rank

        candidate.save()

    @staticmethod
    def reject_draw(candidate: PassedCandidate) -> None:
        if candidate.status != PassedCandidateStatus.drawn:
            raise DomainException(f"Can't reject draw for candidate in status {candidate.status}.")

        Domain.update_status(candidate, PassedCandidateStatus.passed_test)

    @staticmethod
    def select() -> None:
        from payments.domain import Domain as PaymentsDomain

        for candidate in DomainQueries.get_drawn():
            try:
                PaymentsDomain.create_payment(candidate.user.profile)
                Domain.update_status(candidate, PassedCandidateStatus.selected)
            except Exception:
                logger.error(f"failed to create payment for user {candidate.user.email}")


class DomainQueries:
    @staticmethod
    def get_all() -> Any:
        return PassedCandidate.objects.all()

    @staticmethod
    def get_by_status_in(status_list: List[str]) -> Any:
        return PassedCandidate.objects.filter(status__in=status_list)

    @staticmethod
    def get_passed_test() -> Any:
        return PassedCandidate.objects.filter(status=PassedCandidateStatus.passed_test)

    @staticmethod
    def get_drawn() -> Any:
        """Used to show the candidates in the second table of the selection page"""
        return PassedCandidate.objects.filter(status=PassedCandidateStatus.drawn)

    @staticmethod
    def get_selected() -> Any:
        return PassedCandidate.objects.filter(status=PassedCandidateStatus.selected)

    @staticmethod
    def get_accepted() -> Any:
        return PassedCandidate.objects.filter(status=PassedCandidateStatus.accepted)

    @staticmethod
    def get_rejected() -> Any:
        return PassedCandidate.objects.filter(status=PassedCandidateStatus.rejected)

    @staticmethod
    def get_not_selected() -> Any:
        return PassedCandidate.objects.filter(status=PassedCandidateStatus.not_selected)

    @staticmethod
    def get_selected_accepted() -> Any:
        """Used to show the candidates in the first table of the selection page"""
        return PassedCandidate.objects.filter(
            status__in=[PassedCandidateStatus.selected, PassedCandidateStatus.accepted]
        )

    @staticmethod
    def get_max_rank(q: QuerySet) -> int:
        return q.aggregate(Max("draw_rank"))["draw_rank__max"] or 0

    @staticmethod
    def get_drawn_selected_accepted() -> Any:
        return PassedCandidate.objects.filter(
            status__in=[PassedCandidateStatus.drawn, PassedCandidateStatus.selected, PassedCandidateStatus.accepted]
        )

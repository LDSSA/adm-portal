from typing import List

from django.test import TestCase

from payments.models import Payment
from profiles.models import Profile
from selected.domain import Domain, DomainException, DomainQueries, DrawCounters, DrawParams
from selected.models import PassedCandidate, PassedCandidateStatus
from users.models import User


class TestDomain(TestCase):
    def test_must_pick_female(self) -> None:
        params = DrawParams(number_of_seats=50, min_female_quota=0.35, max_company_quota=0.2)

        tt = [
            {"total": 0, "female": 0, "expected": True},
            {"total": 1, "female": 1, "expected": False},
            {"total": 2, "female": 1, "expected": True},
        ]

        for t in tt:
            counters = DrawCounters()
            counters.total = t["total"]
            counters.female = t["female"]

            self.assertEqual(Domain.must_pick_female(params, counters), t["expected"])

    def test_must_not_pick_company(self) -> None:
        params = DrawParams(number_of_seats=50, min_female_quota=0.35, max_company_quota=0.2)

        tt = [{"total": 0, "company": 0, "expected": True}, {"total": 40, "company": 5, "expected": False}]

        for t in tt:
            counters = DrawCounters()
            counters.total = t["total"]
            counters.company = t["company"]

            self.assertEqual(Domain.must_not_pick_company(params, counters), t["expected"])

    def test_draw_all_females(self) -> None:
        params = DrawParams(number_of_seats=10, min_female_quota=1, max_company_quota=0)

        for i in range(15):
            u = User.objects.create(email=f"female_user_{i}@amd.com")
            Profile.objects.create(user=u, ticket_type="regular", gender="f")
            PassedCandidate.objects.create(user=u, status=PassedCandidateStatus.passed_test)

        Domain.draw(params)

        self.assertEqual(DomainQueries.get_drawn().count(), 10)
        self.assertEqual(DomainQueries.get_drawn().filter(user__profile__gender="f").count(), 10)
        self.assertEqual(DomainQueries.get_passed_test().count(), 5)

    def test_draw_all_females_not_enough(self) -> None:
        params = DrawParams(number_of_seats=10, min_female_quota=1, max_company_quota=0)

        for i in range(9):
            u = User.objects.create(email=f"female_user_{i}@amd.com")
            Profile.objects.create(user=u, ticket_type="regular", gender="f")
            PassedCandidate.objects.create(user=u, status=PassedCandidateStatus.passed_test)

            u = User.objects.create(email=f"male_user_{i}@amd.com")
            Profile.objects.create(user=u, ticket_type="regular", gender="m")
            PassedCandidate.objects.create(user=u, status=PassedCandidateStatus.passed_test)

        Domain.draw(params)

        self.assertEqual(DomainQueries.get_drawn().count(), 10)
        self.assertEqual(DomainQueries.get_drawn().filter(user__profile__gender="f").count(), 9)
        self.assertEqual(DomainQueries.get_drawn().filter(user__profile__gender="m").count(), 1)
        self.assertEqual(DomainQueries.get_passed_test().count(), 8)

    def test_draw_1pc_females(self) -> None:
        params = DrawParams(number_of_seats=6, min_female_quota=0.01, max_company_quota=0)

        for i in range(9):
            u = User.objects.create(email=f"female_user_{i}@amd.com")
            Profile.objects.create(user=u, ticket_type="regular", gender="f")
            PassedCandidate.objects.create(user=u, status=PassedCandidateStatus.passed_test)

            u = User.objects.create(email=f"male_user_{i}@amd.com")
            Profile.objects.create(user=u, ticket_type="regular", gender="m")
            PassedCandidate.objects.create(user=u, status=PassedCandidateStatus.passed_test)

        Domain.draw(params)

        self.assertEqual(DomainQueries.get_drawn().count(), 6)
        self.assertTrue(DomainQueries.get_drawn().filter(user__profile__gender="f").count() > 0)

    def test_draw_0_companies(self) -> None:
        params = DrawParams(number_of_seats=8, min_female_quota=0, max_company_quota=0)

        for i in range(9):
            u = User.objects.create(email=f"company_female_user_{i}@amd.com")
            Profile.objects.create(user=u, ticket_type="company", gender="f")
            PassedCandidate.objects.create(user=u, status=PassedCandidateStatus.passed_test)

            u = User.objects.create(email=f"male_user_{i}@amd.com")
            Profile.objects.create(user=u, ticket_type="regular", gender="m")
            PassedCandidate.objects.create(user=u, status=PassedCandidateStatus.passed_test)

            u = User.objects.create(email=f"student_male_user_{i}@amd.com")
            Profile.objects.create(user=u, ticket_type="student", gender="m")
            PassedCandidate.objects.create(user=u, status=PassedCandidateStatus.passed_test)

        Domain.draw(params)

        self.assertEqual(DomainQueries.get_drawn().count(), 8)
        self.assertEqual(DomainQueries.get_drawn().filter(user__profile__ticket_type="company").count(), 0)

    def test_draw_rejects_dont_count(self) -> None:
        params = DrawParams(number_of_seats=10, min_female_quota=1, max_company_quota=0)

        for i in range(100):
            u = User.objects.create(email=f"rejected_female_user_{i}@amd.com")
            Profile.objects.create(user=u, ticket_type="regular", gender="f")
            PassedCandidate.objects.create(user=u, status=PassedCandidateStatus.rejected)

            u = User.objects.create(email=f"male_user_{i}@amd.com")
            Profile.objects.create(user=u, ticket_type="regular", gender="m")
            PassedCandidate.objects.create(user=u, status=PassedCandidateStatus.passed_test)

        to_be_selected_candidates: List[PassedCandidate] = []
        for i in range(10):
            u = User.objects.create(email=f"female_user_{i}@amd.com")
            Profile.objects.create(user=u, ticket_type="regular", gender="f")
            to_be_selected_candidates.append(
                PassedCandidate.objects.create(user=u, status=PassedCandidateStatus.passed_test)
            )

        Domain.draw(params)

        self.assertEqual(DomainQueries.get_drawn().count(), 10)
        self.assertEqual(DomainQueries.get_drawn().filter(user__profile__gender="f").count(), 10)
        for candidate in to_be_selected_candidates:
            candidate.refresh_from_db()
            self.assertEqual(candidate.status, PassedCandidateStatus.drawn)

    def test_draw_none(self) -> None:
        params = DrawParams(number_of_seats=8, min_female_quota=0, max_company_quota=0)

        for i in range(2):
            u = User.objects.create(email=f"female_user_{i}@amd.com")
            Profile.objects.create(user=u, ticket_type="regular", gender="f")
            PassedCandidate.objects.create(user=u, status=PassedCandidateStatus.passed_test)

            u = User.objects.create(email=f"selected_female_user_{i}@amd.com")
            Profile.objects.create(user=u, ticket_type="regular", gender="f")
            PassedCandidate.objects.create(user=u, status=PassedCandidateStatus.selected)

            u = User.objects.create(email=f"accpeted_female_user_{i}@amd.com")
            Profile.objects.create(user=u, ticket_type="regular", gender="f")
            PassedCandidate.objects.create(user=u, status=PassedCandidateStatus.accepted)

            u = User.objects.create(email=f"male_user_{i}@amd.com")
            Profile.objects.create(user=u, ticket_type="regular", gender="m")
            PassedCandidate.objects.create(user=u, status=PassedCandidateStatus.passed_test)

            u = User.objects.create(email=f"selected_male_user_{i}@amd.com")
            Profile.objects.create(user=u, ticket_type="regular", gender="m")
            PassedCandidate.objects.create(user=u, status=PassedCandidateStatus.selected)

            u = User.objects.create(email=f"accepted_male_user_{i}@amd.com")
            Profile.objects.create(user=u, ticket_type="regular", gender="m")
            PassedCandidate.objects.create(user=u, status=PassedCandidateStatus.accepted)

        Domain.draw(params)

        self.assertEqual(DomainQueries.get_drawn().count(), 0)

    def test_draw_real(self) -> None:
        params = DrawParams(number_of_seats=50, min_female_quota=0.35, max_company_quota=0.1)

        for i in range(100):
            u = User.objects.create(email=f"male_user_{i}@amd.com")
            Profile.objects.create(user=u, ticket_type="regular", gender="m")
            PassedCandidate.objects.create(user=u, status=PassedCandidateStatus.passed_test)

        for i in range(30):
            u = User.objects.create(email=f"company_male_user_{i}@amd.com")
            Profile.objects.create(user=u, ticket_type="company", gender="m")
            PassedCandidate.objects.create(user=u, status=PassedCandidateStatus.passed_test)

        for i in range(15):
            u = User.objects.create(email=f"student_male_user_{i}@amd.com")
            Profile.objects.create(user=u, ticket_type="student", gender="m")
            PassedCandidate.objects.create(user=u, status=PassedCandidateStatus.passed_test)

        for i in range(20):
            u = User.objects.create(email=f"female_user_{i}@amd.com")
            Profile.objects.create(user=u, ticket_type="regular", gender="f")
            PassedCandidate.objects.create(user=u, status=PassedCandidateStatus.passed_test)

        for i in range(5):
            u = User.objects.create(email=f"company_female_user_{i}@amd.com")
            Profile.objects.create(user=u, ticket_type="company", gender="f")
            PassedCandidate.objects.create(user=u, status=PassedCandidateStatus.passed_test)

        for i in range(7):
            u = User.objects.create(email=f"student_female_user_{i}@amd.com")
            Profile.objects.create(user=u, ticket_type="student", gender="f")
            PassedCandidate.objects.create(user=u, status=PassedCandidateStatus.passed_test)

        Domain.draw(params)

        self.assertEqual(DomainQueries.get_drawn().count(), 50)
        self.assertTrue(
            DomainQueries.get_drawn().filter(user__profile__gender="f").count()
            > params.number_of_seats * params.min_female_quota
        )
        self.assertTrue(
            DomainQueries.get_drawn().filter(user__profile__ticket_type="company").count()
            < params.number_of_seats * params.max_company_quota
        )

    def test_reject_draw(self) -> None:
        u = User.objects.create(email=f"drawn_female_user@amd.com")
        Profile.objects.create(user=u, ticket_type="company", gender="f")
        candidate = PassedCandidate.objects.create(user=u, status=PassedCandidateStatus.drawn)

        Domain.reject_draw(candidate)

        self.assertEqual(DomainQueries.get_drawn().count(), 0)
        self.assertEqual(DomainQueries.get_passed_test().count(), 1)

    def test_reject_draw_expection(self) -> None:
        u = User.objects.create(email=f"selected_female_user@amd.com")
        Profile.objects.create(user=u, ticket_type="company", gender="f")
        candidate = PassedCandidate.objects.create(user=u, status=PassedCandidateStatus.selected)

        with self.assertRaises(DomainException):
            Domain.reject_draw(candidate)

    def test_select(self) -> None:
        for i in range(9):
            u = User.objects.create(email=f"female_user_{i}@amd.com")
            Profile.objects.create(user=u, ticket_type="company", gender="f")
            PassedCandidate.objects.create(user=u, status=PassedCandidateStatus.passed_test)

            u = User.objects.create(email=f"drawn_female_user_{i}@amd.com")
            Profile.objects.create(user=u, ticket_type="company", gender="f")
            PassedCandidate.objects.create(user=u, status=PassedCandidateStatus.drawn)

        Domain.select()

        self.assertEqual(Payment.objects.all().count(), 9)
        self.assertEqual(DomainQueries.get_selected().filter(status="selected").count(), 9)


class TestQueries(TestCase):
    def test_draw_rank(self) -> None:
        PassedCandidate.objects.create(
            user=User.objects.create(email=f"u1@user.com"), status=PassedCandidateStatus.passed_test
        )
        PassedCandidate.objects.create(
            user=User.objects.create(email=f"u2@user.com"), status=PassedCandidateStatus.selected, draw_rank=1
        )
        PassedCandidate.objects.create(
            user=User.objects.create(email=f"u3@user.com"), status=PassedCandidateStatus.drawn, draw_rank=3
        )
        PassedCandidate.objects.create(
            user=User.objects.create(email=f"u4@user.com"), status=PassedCandidateStatus.accepted, draw_rank=2
        )
        PassedCandidate.objects.create(
            user=User.objects.create(email=f"u5@user.com"), status=PassedCandidateStatus.selected, draw_rank=4
        )

        tt = [
            {"q": PassedCandidate.objects.filter(status="404notfound"), "expected": 0},
            {"q": PassedCandidate.objects.filter(status=PassedCandidateStatus.passed_test), "expected": 0},
            {"q": PassedCandidate.objects.filter(status=PassedCandidateStatus.drawn), "expected": 3},
            {"q": PassedCandidate.objects.all(), "expected": 4},
        ]

        for t in tt:
            max_rank = DomainQueries.get_max_rank(t["q"])
            self.assertEqual(max_rank, t["expected"])

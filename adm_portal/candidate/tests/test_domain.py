from django.test import TestCase

from applications.domain import ApplicationStatus, SubmissionStatus
from applications.models import Application
from candidate.domain import CandidateState, Domain
from profiles.models import Profile
from selection.models import Selection
from selection.status import SelectionStatus
from users.models import User


class TestDomain(TestCase):
    def test_candidate_state_defaults(self) -> None:
        candidate_state = CandidateState()
        self.assertEqual(candidate_state.signed_up, False)
        self.assertEqual(candidate_state.confirmed_email, False)
        self.assertEqual(candidate_state.created_profile, False)
        self.assertEqual(candidate_state.accepted_coc, False)
        self.assertIsNone(candidate_state.application_status)
        self.assertIsNone(candidate_state.coding_test_status)
        self.assertIsNone(candidate_state.slu01_status)
        self.assertIsNone(candidate_state.slu02_status)
        self.assertIsNone(candidate_state.slu03_status)
        self.assertIsNone(candidate_state.selection_status)

    def test_get_candidate_state(self) -> None:
        candidate = User(email="candidate@adm.com")
        self.assertEqual(Domain.get_candidate_state(candidate)._asdict(), CandidateState()._asdict())

        candidate = User.objects.create(email="candidate@adm.com", email_confirmed=True, code_of_conduct_accepted=True)
        Profile.objects.create(user=candidate)
        Application.objects.create(user=candidate)
        Selection.objects.create(user=candidate)

        self.assertEqual(
            Domain.get_candidate_state(candidate),
            CandidateState(
                signed_up=True,
                confirmed_email=True,
                created_profile=True,
                accepted_coc=True,
                application_status=ApplicationStatus.ongoing,
                coding_test_status=SubmissionStatus.not_started,
                slu01_status=SubmissionStatus.ongoing,
                slu02_status=SubmissionStatus.ongoing,
                slu03_status=SubmissionStatus.ongoing,
                selection_status=SelectionStatus.PASSED_TEST,
            ),
        )

    def test_candidate_state_readable(self) -> None:
        expected = {
            "signed_up": "Signed Up",
            "confirmed_email": "Confirmed Email",
            "created_profile": "Created Profile",
            "accepted_coc": "Accepted Coc",
            "application_status": "Application Status",
            "coding_test_status": "Coding Test Status",
            "slu01_status": "SLU 01 Status",
            "slu02_status": "SLU 02 Status",
            "slu03_status": "SLU 03 Status",
            "selection_status": "Selection Status",
        }

        readable = Domain.candidate_state_readable(CandidateState())
        self.assertEqual(readable, expected)

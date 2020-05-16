from datetime import datetime, timedelta

from django.test import TestCase

from applications.models import Application, Submission, SubmissionTypes
from interface import interface
from selected.models import PassedCandidate, PassedCandidateStatus
from staff.domain import Events, EventsException
from users.models import User


class TestEvents(TestCase):
    def setUp(self) -> None:
        self.aod = datetime.now() - timedelta(minutes=30)
        self.acd = datetime.now() + timedelta(minutes=30)
        interface.feature_flag_client.set_applications_opening_date(self.aod)
        interface.feature_flag_client.set_applications_closing_date(self.acd)

    def test_trigger_applications_are_over_exception(self) -> None:
        # because applications are not closed
        with self.assertRaises(EventsException):
            Events.trigger_applications_are_over()

    def test_trigger_applications_are_over(self) -> None:
        interface.feature_flag_client.set_applications_opening_date(self.aod - timedelta(minutes=60))
        interface.feature_flag_client.set_applications_closing_date(self.acd - timedelta(minutes=60))

        a1 = Application.objects.create(user=User.objects.create(email="a1@test.com"))
        a2 = Application.objects.create(user=User.objects.create(email="a2@test.com"))
        a3 = Application.objects.create(user=User.objects.create(email="a3@test.com"))

        a4 = Application.objects.create(user=User.objects.create(email="a4@test.com"))
        Submission.objects.create(application=a4, score=99, submission_type=SubmissionTypes.coding_test.uname)
        Submission.objects.create(application=a4, score=99, submission_type=SubmissionTypes.slu01.uname)
        Submission.objects.create(application=a4, score=99, submission_type=SubmissionTypes.slu02.uname)
        Submission.objects.create(application=a4, score=99, submission_type=SubmissionTypes.slu03.uname)

        a5 = Application.objects.create(
            user=User.objects.create(email="a5@test.com"), application_over_email_sent="passed"
        )

        self.assertEqual(Events.applications_are_over_total_emails(), 5)
        self.assertEqual(Events.applications_are_over_sent_emails(), 1)

        self.assertIsNone(a1.application_over_email_sent)
        self.assertIsNone(a2.application_over_email_sent)
        self.assertIsNone(a3.application_over_email_sent)
        self.assertIsNone(a4.application_over_email_sent)
        self.assertEqual(a5.application_over_email_sent, "passed")

        Events.trigger_applications_are_over()

        self.assertEqual(Events.applications_are_over_total_emails(), 5)
        self.assertEqual(Events.applications_are_over_sent_emails(), 5)

        a1.refresh_from_db()
        self.assertEqual(a1.application_over_email_sent, "failed")
        a2.refresh_from_db()
        self.assertEqual(a2.application_over_email_sent, "failed")
        a3.refresh_from_db()
        self.assertEqual(a3.application_over_email_sent, "failed")
        a4.refresh_from_db()
        self.assertEqual(a4.application_over_email_sent, "passed")
        a5.refresh_from_db()
        self.assertEqual(a5.application_over_email_sent, "passed")

    def test_trigger_admissions_are_over_exception(self) -> None:
        # because applications are not closed
        with self.assertRaises(EventsException):
            Events.trigger_admissions_are_over()

        interface.feature_flag_client.set_applications_opening_date(self.aod - timedelta(minutes=60))
        interface.feature_flag_client.set_applications_closing_date(self.acd - timedelta(minutes=60))

        c = PassedCandidate.objects.create(
            user=User.objects.create(email="u1@test.com"), status=PassedCandidateStatus.drawn
        )

        # because the is a drawn candidate
        with self.assertRaises(EventsException):
            Events.trigger_admissions_are_over()

        c.status = PassedCandidateStatus.selected
        c.save()

        # because the is a selected candidate
        with self.assertRaises(EventsException):
            Events.trigger_admissions_are_over()

    def test_trigger_admissions_are_over(self) -> None:
        interface.feature_flag_client.set_applications_opening_date(self.aod - timedelta(minutes=60))
        interface.feature_flag_client.set_applications_closing_date(self.acd - timedelta(minutes=60))

        PassedCandidate.objects.create(
            user=User.objects.create(email="u1@test.com"), status=PassedCandidateStatus.passed_test
        )

        PassedCandidate.objects.create(
            user=User.objects.create(email="u2@test.com"), status=PassedCandidateStatus.accepted
        )

        PassedCandidate.objects.create(
            user=User.objects.create(email="u3@test.com"), status=PassedCandidateStatus.rejected
        )

        self.assertEqual(PassedCandidate.objects.filter(status=PassedCandidateStatus.passed_test).count(), 1)
        self.assertEqual(PassedCandidate.objects.filter(status=PassedCandidateStatus.accepted).count(), 1)
        self.assertEqual(PassedCandidate.objects.filter(status=PassedCandidateStatus.rejected).count(), 1)
        self.assertEqual(PassedCandidate.objects.filter(status=PassedCandidateStatus.not_selected).count(), 0)

        Events.trigger_admissions_are_over()

        self.assertEqual(PassedCandidate.objects.filter(status=PassedCandidateStatus.passed_test).count(), 0)
        self.assertEqual(PassedCandidate.objects.filter(status=PassedCandidateStatus.accepted).count(), 1)
        self.assertEqual(PassedCandidate.objects.filter(status=PassedCandidateStatus.rejected).count(), 1)
        self.assertEqual(PassedCandidate.objects.filter(status=PassedCandidateStatus.not_selected).count(), 1)

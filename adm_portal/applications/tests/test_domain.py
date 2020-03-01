from datetime import datetime, timedelta

from django.test import TestCase

from applications.domain import Domain, DomainException, SubmissionStatus
from applications.models import Application, Submission, SubmissionTypes
from users.models import User


class TestDomain(TestCase):
    def test_get_start_date(self) -> None:
        a = Application.objects.create(user=User.objects.create(email="target@test.com"))

        expected_slu_start_date = datetime(day=21, month=6, year=2020)
        self.assertEqual(Domain.get_start_date(a, SubmissionTypes.coding_test), None)
        self.assertEqual(Domain.get_start_date(a, SubmissionTypes.slu01), expected_slu_start_date)
        self.assertEqual(Domain.get_start_date(a, SubmissionTypes.slu02), expected_slu_start_date)
        self.assertEqual(Domain.get_start_date(a, SubmissionTypes.slu03), expected_slu_start_date)

        now = datetime.now()
        a.coding_test_started_at = now
        a.save()
        self.assertEqual(Domain.get_start_date(a, SubmissionTypes.coding_test), now)

    def test_get_close_date(self) -> None:
        a = Application.objects.create(user=User.objects.create(email="target@test.com"))

        expected_slu_start_date = datetime(day=21, month=6, year=2020)
        expected_coding_test_delta = timedelta(hours=2)
        expected_slu_delta = timedelta(days=14)
        expected_domain_buffer_delta = timedelta(minutes=2)
        with self.assertRaises(DomainException):
            Domain.get_close_date(a, SubmissionTypes.coding_test)

        self.assertEqual(Domain.get_close_date(a, SubmissionTypes.slu01), expected_slu_start_date + expected_slu_delta)
        self.assertEqual(
            Domain.get_close_date(a, SubmissionTypes.slu01, apply_buffer=True),
            expected_slu_start_date + expected_slu_delta + expected_domain_buffer_delta,
        )

        self.assertEqual(Domain.get_close_date(a, SubmissionTypes.slu02), expected_slu_start_date + expected_slu_delta)
        self.assertEqual(
            Domain.get_close_date(a, SubmissionTypes.slu02, apply_buffer=True),
            expected_slu_start_date + expected_slu_delta + expected_domain_buffer_delta,
        )

        self.assertEqual(Domain.get_close_date(a, SubmissionTypes.slu03), expected_slu_start_date + expected_slu_delta)
        self.assertEqual(
            Domain.get_close_date(a, SubmissionTypes.slu03, apply_buffer=True),
            expected_slu_start_date + expected_slu_delta + expected_domain_buffer_delta,
        )

        now = datetime.now()
        a.coding_test_started_at = now
        a.save()
        self.assertEqual(Domain.get_close_date(a, SubmissionTypes.coding_test), now + expected_coding_test_delta)
        self.assertEqual(
            Domain.get_close_date(a, SubmissionTypes.coding_test, apply_buffer=True),
            now + expected_coding_test_delta + expected_domain_buffer_delta,
        )

    def test_get_best_score(self) -> None:
        target_app = Application.objects.create(user=User.objects.create(email="target@test.com"))
        other_app = Application.objects.create(user=User.objects.create(email="other@test.com"))
        Submission.objects.create(application=target_app, score=10, submission_type=SubmissionTypes.coding_test.uname)
        Submission.objects.create(application=target_app, score=89, submission_type=SubmissionTypes.coding_test.uname)

        Submission.objects.create(application=target_app, score=73, submission_type=SubmissionTypes.slu01.uname)

        Submission.objects.create(application=target_app, score=71, submission_type=SubmissionTypes.slu03.uname)
        Submission.objects.create(application=target_app, score=21, submission_type=SubmissionTypes.slu03.uname)
        Submission.objects.create(application=target_app, score=92, submission_type=SubmissionTypes.slu03.uname)

        self.assertEqual(Domain.get_best_score(target_app, SubmissionTypes.coding_test), 89)
        self.assertEqual(Domain.get_best_score(target_app, SubmissionTypes.slu01), 73)
        self.assertEqual(Domain.get_best_score(target_app, SubmissionTypes.slu02), None)
        self.assertEqual(Domain.get_best_score(target_app, SubmissionTypes.slu03), 92)

        self.assertEqual(Domain.get_best_score(other_app, SubmissionTypes.coding_test), None)
        self.assertEqual(Domain.get_best_score(other_app, SubmissionTypes.slu01), None)
        self.assertEqual(Domain.get_best_score(other_app, SubmissionTypes.slu02), None)
        self.assertEqual(Domain.get_best_score(other_app, SubmissionTypes.slu03), None)

    def test_has_positive_score(self) -> None:
        target_app = Application.objects.create(user=User.objects.create(email="target@test.com"))
        other_app = Application.objects.create(user=User.objects.create(email="other@test.com"))
        Submission.objects.create(application=target_app, score=10, submission_type=SubmissionTypes.coding_test.uname)
        Submission.objects.create(application=target_app, score=89, submission_type=SubmissionTypes.coding_test.uname)

        Submission.objects.create(application=target_app, score=73, submission_type=SubmissionTypes.slu01.uname)

        Submission.objects.create(application=target_app, score=71, submission_type=SubmissionTypes.slu03.uname)
        Submission.objects.create(application=target_app, score=21, submission_type=SubmissionTypes.slu03.uname)
        Submission.objects.create(application=target_app, score=92, submission_type=SubmissionTypes.slu03.uname)

        self.assertEqual(Domain.has_positive_score(target_app, SubmissionTypes.coding_test), True)
        self.assertEqual(Domain.has_positive_score(target_app, SubmissionTypes.slu01), False)
        self.assertEqual(Domain.has_positive_score(target_app, SubmissionTypes.slu02), False)
        self.assertEqual(Domain.has_positive_score(target_app, SubmissionTypes.slu03), True)

        self.assertEqual(Domain.has_positive_score(other_app, SubmissionTypes.coding_test), False)
        self.assertEqual(Domain.has_positive_score(other_app, SubmissionTypes.slu01), False)
        self.assertEqual(Domain.has_positive_score(other_app, SubmissionTypes.slu02), False)
        self.assertEqual(Domain.has_positive_score(other_app, SubmissionTypes.slu03), False)

    def test_get_sub_type_status(self) -> None:
        a = Application.objects.create(user=User.objects.create(email="target@test.com"))

        self.assertEqual(Domain.get_sub_type_status(a, SubmissionTypes.coding_test), SubmissionStatus.not_started)
        self.assertEqual(Domain.get_sub_type_status(a, SubmissionTypes.slu01), SubmissionStatus.ongoing)
        self.assertEqual(Domain.get_sub_type_status(a, SubmissionTypes.slu02), SubmissionStatus.ongoing)
        self.assertEqual(Domain.get_sub_type_status(a, SubmissionTypes.slu03), SubmissionStatus.ongoing)

        Submission.objects.create(application=a, score=99, submission_type=SubmissionTypes.slu01.uname)
        self.assertEqual(Domain.get_sub_type_status(a, SubmissionTypes.slu01), SubmissionStatus.passed)

        a.slu02_started_at = datetime.now() - timedelta(days=20)
        a.save()
        self.assertEqual(Domain.get_sub_type_status(a, SubmissionTypes.slu02), SubmissionStatus.failed)

    def test_add_submission(self) -> None:
        a = Application.objects.create(user=User.objects.create(email="target@test.com"))
        s1 = Submission(score=91)
        s2 = Submission(score=92)
        s3 = Submission(score=93)

        a.coding_test_started_at = None
        a.save()
        with self.assertRaises(DomainException):
            Domain.add_submission(a, SubmissionTypes.coding_test, s1)
        self.assertEqual(a.submissions.count(), 0)

        a.coding_test_started_at = datetime.now()
        a.save()
        Domain.add_submission(a, SubmissionTypes.coding_test, s2)
        self.assertEqual(a.submissions.count(), 1)

        a.coding_test_started_at = datetime.now() - timedelta(hours=3)
        a.save()

        with self.assertRaises(DomainException):
            Domain.add_submission(a, SubmissionTypes.coding_test, s3)
        self.assertEqual(a.submissions.count(), 1)
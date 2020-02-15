from datetime import datetime, timedelta

from django.test import TestCase

from applications.models import Application, Submission, SubmissionsClosedException, SubmissionsNotOpenException
from users.models import User


class TestApplicationModel(TestCase):
    def setUp(self) -> None:
        self.now = datetime.now()

        self.u1 = User.objects.create(email="u1@test.com")
        self.u2 = User.objects.create(email="u2@test.com")
        self.u3 = User.objects.create(email="u3@test.com")
        self.u4 = User.objects.create(email="u4@test.com")

        self.a1 = Application.objects.create(user=self.u1)
        self.a2 = Application.objects.create(user=self.u2)
        self.a3 = Application.objects.create(user=self.u3)
        self.a4 = Application.objects.create(user=self.u4)

    def test_new_coding_test_submission(self) -> None:
        now = self.now

        one_hour_ago = now - timedelta(hours=1)
        self.a1.coding_test_started_at = one_hour_ago
        self.a1.save()

        self.a1.coding_test_new_submission(submission=Submission())

        two_hours_ago = now - timedelta(hours=2)
        self.a2.coding_test_started_at = two_hours_ago
        self.a2.save()

        self.a2.coding_test_new_submission(submission=Submission())

        two_hours_and_five_minutes_ago = now - timedelta(hours=2, minutes=5)
        self.a3.coding_test_started_at = two_hours_and_five_minutes_ago
        self.a3.save()

        with self.assertRaises(expected_exception=SubmissionsClosedException):
            self.a3.coding_test_new_submission(submission=Submission())

        with self.assertRaises(expected_exception=SubmissionsNotOpenException):
            self.a4.coding_test_new_submission(submission=Submission())

    def test_coding_test_status(self) -> None:
        now = self.now

        self.assertEqual(self.a1.coding_test_status, "to do")

        self.a2.coding_test_started_at = now  # just to add submissions
        self.a2.coding_test_new_submission(submission=Submission(score=1))
        self.a2.coding_test_new_submission(submission=Submission(score=90))
        one_hour_ago = now - timedelta(hours=1)
        self.a2.coding_test_started_at = one_hour_ago
        self.a2.save()
        self.assertEqual(self.a2.coding_test_status, "ongoing")

        self.a3.coding_test_started_at = now  # just to add submissions
        self.a3.coding_test_new_submission(submission=Submission(score=1))
        self.a3.coding_test_new_submission(submission=Submission(score=75))
        three_hours_ago = now - timedelta(hours=3)
        self.a3.coding_test_started_at = three_hours_ago
        self.a3.save()
        self.assertEqual(self.a3.coding_test_status, "finished")

        self.a4.coding_test_started_at = now  # just to add submissions
        self.a4.coding_test_new_submission(submission=Submission(score=0))
        self.a4.coding_test_new_submission(submission=Submission(score=20))
        self.a4.coding_test_new_submission(submission=Submission(score=69))
        three_hours_ago = now - timedelta(hours=3)
        self.a4.coding_test_started_at = three_hours_ago
        self.a4.save()
        self.assertEqual(self.a4.coding_test_status, "finished")

    def test_coding_test_best_score(self) -> None:
        self.a1.coding_test_started_at = self.now  # just to add submissions
        self.a1.coding_test_new_submission(submission=Submission(score=10))
        self.a1.coding_test_new_submission(submission=Submission(score=89))

        self.a2.coding_test_started_at = self.now  # just to add submissions
        self.a2.coding_test_new_submission(submission=Submission(score=51))
        self.a2.coding_test_new_submission(submission=Submission(score=94))
        self.a2.coding_test_new_submission(submission=Submission(score=1))

        self.assertEqual(self.a1.coding_test_best_score, 89)
        self.assertEqual(self.a2.coding_test_best_score, 94)
        self.assertEqual(self.a3.coding_test_best_score, None)

    def test_coding_test_passed(self) -> None:
        self.a1.coding_test_started_at = self.now  # just to add submissions
        self.a1.coding_test_new_submission(submission=Submission(score=10))
        self.a1.coding_test_new_submission(submission=Submission(score=75))
        self.a1.coding_test_new_submission(submission=Submission(score=51))

        self.a2.coding_test_started_at = self.now  # just to add submissions
        self.a2.coding_test_new_submission(submission=Submission(score=94))
        self.a2.coding_test_new_submission(submission=Submission(score=2))

        self.a3.coding_test_started_at = self.now  # just to add submissions
        self.a3.coding_test_new_submission(submission=Submission(score=74))

        self.assertTrue(self.a1.coding_test_passed)
        self.assertTrue(self.a2.coding_test_passed)
        self.assertFalse(self.a3.coding_test_passed)
        self.assertFalse(self.a4.coding_test_passed)

from datetime import datetime, timedelta

from django.test import TestCase

from applications.models import (
    Application,
    CodingTestSubmission,
    CodingTestSubmissionsClosedException,
    CodingTestSubmissionsNotOpenException,
)
from users.models import User


class TestApplicationModel(TestCase):
    def setUp(self) -> None:
        self.u1 = User.objects.create(email="u1@test.com")
        self.u2 = User.objects.create(email="u2@test.com")
        self.u3 = User.objects.create(email="u3@test.com")
        self.u4 = User.objects.create(email="u4@test.com")

        self.a1 = Application.objects.create(user=self.u1)
        self.a2 = Application.objects.create(user=self.u2)
        self.a3 = Application.objects.create(user=self.u3)
        self.a4 = Application.objects.create(user=self.u4)

    def test_new_coding_test_submission(self) -> None:
        now = datetime.now()

        one_hour_ago = now - timedelta(hours=1)
        self.a1.coding_test_downloaded_at = one_hour_ago
        self.a1.save()

        self.a1.new_coding_test_submission(submission=CodingTestSubmission())

        two_hours_ago = now - timedelta(hours=2)
        self.a2.coding_test_downloaded_at = two_hours_ago
        self.a2.save()

        self.a2.new_coding_test_submission(submission=CodingTestSubmission())

        two_hours_and_five_minutes_ago = now - timedelta(hours=2, minutes=5)
        self.a3.coding_test_downloaded_at = two_hours_and_five_minutes_ago
        self.a3.save()

        with self.assertRaises(expected_exception=CodingTestSubmissionsClosedException):
            self.a3.new_coding_test_submission(submission=CodingTestSubmission())

        with self.assertRaises(expected_exception=CodingTestSubmissionsNotOpenException):
            self.a4.new_coding_test_submission(submission=CodingTestSubmission())

    def test_coding_test_status(self) -> None:
        now = datetime.now()

        self.assertEqual(self.a1.coding_test_status, "to do")

        one_hour_ago = now - timedelta(hours=1)
        self.a2.coding_test_downloaded_at = one_hour_ago
        self.a2.save()
        CodingTestSubmission.objects.create(application=self.a2, score=1)
        CodingTestSubmission.objects.create(application=self.a2, score=90)
        self.assertEqual(self.a2.coding_test_status, "ongoing")

        three_hours_ago = now - timedelta(hours=3)
        self.a3.coding_test_downloaded_at = three_hours_ago
        self.a3.save()
        CodingTestSubmission.objects.create(application=self.a3, score=1)
        CodingTestSubmission.objects.create(application=self.a3, score=75)
        self.assertEqual(self.a3.coding_test_status, "finished")

        three_hours_ago = now - timedelta(hours=3)
        self.a4.coding_test_downloaded_at = three_hours_ago
        self.a4.save()
        CodingTestSubmission.objects.create(application=self.a4, score=1)
        CodingTestSubmission.objects.create(application=self.a4, score=20)
        CodingTestSubmission.objects.create(application=self.a4, score=69)
        self.assertEqual(self.a4.coding_test_status, "finished")

    def test_coding_test_best_score(self) -> None:
        CodingTestSubmission.objects.create(application=self.a1, score=10)
        CodingTestSubmission.objects.create(application=self.a1, score=89)
        CodingTestSubmission.objects.create(application=self.a1, score=51)

        CodingTestSubmission.objects.create(application=self.a2, score=94)
        CodingTestSubmission.objects.create(application=self.a2, score=1)

        self.assertEqual(self.a1.coding_test_best_score, 89)
        self.assertEqual(self.a2.coding_test_best_score, 94)
        self.assertEqual(self.a3.coding_test_best_score, None)

    def test_coding_test_passed(self) -> None:
        CodingTestSubmission.objects.create(application=self.a1, score=10)
        CodingTestSubmission.objects.create(application=self.a1, score=75)
        CodingTestSubmission.objects.create(application=self.a1, score=51)

        CodingTestSubmission.objects.create(application=self.a2, score=94)
        CodingTestSubmission.objects.create(application=self.a2, score=1)

        CodingTestSubmission.objects.create(application=self.a3, score=74)

        self.assertTrue(self.a1.coding_test_passed)
        self.assertTrue(self.a2.coding_test_passed)
        self.assertFalse(self.a3.coding_test_passed)
        self.assertFalse(self.a4.coding_test_passed)

from datetime import datetime, timedelta

from django.test import TestCase

from applications.models import (
    Application,
    PythonTestSubmission,
    PythonTestSubmissionsClosedException,
    PythonTestSubmissionsNotOpenException,
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

    def test_new_python_test_submission(self) -> None:
        now = datetime.now()

        one_hour_ago = now - timedelta(hours=1)
        self.a1.python_test_downloaded_at = one_hour_ago
        self.a1.save()

        self.a1.new_python_test_submission(submission=PythonTestSubmission())

        two_hours_ago = now - timedelta(hours=2)
        self.a2.python_test_downloaded_at = two_hours_ago
        self.a2.save()

        self.a2.new_python_test_submission(submission=PythonTestSubmission())

        two_hours_and_five_minutes_ago = now - timedelta(hours=2, minutes=5)
        self.a3.python_test_downloaded_at = two_hours_and_five_minutes_ago
        self.a3.save()

        with self.assertRaises(expected_exception=PythonTestSubmissionsClosedException):
            self.a3.new_python_test_submission(submission=PythonTestSubmission())

        with self.assertRaises(expected_exception=PythonTestSubmissionsNotOpenException):
            self.a4.new_python_test_submission(submission=PythonTestSubmission())

    def test_best_python_score(self) -> None:
        PythonTestSubmission.objects.create(application=self.a1, score=10)
        PythonTestSubmission.objects.create(application=self.a1, score=89)
        PythonTestSubmission.objects.create(application=self.a1, score=51)

        PythonTestSubmission.objects.create(application=self.a2, score=94)
        PythonTestSubmission.objects.create(application=self.a2, score=1)

        self.assertEqual(self.a1.best_python_test_score, 89)
        self.assertEqual(self.a2.best_python_test_score, 94)
        self.assertEqual(self.a3.best_python_test_score, None)

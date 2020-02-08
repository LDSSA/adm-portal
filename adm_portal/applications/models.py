from datetime import datetime, timedelta
from logging import getLogger
from typing import Optional

from django.db import models

logger = getLogger(__name__)


class PythonTestSubmission(models.Model):
    application = models.ForeignKey(
        to="applications.Application", on_delete=models.CASCADE, related_name="python_tests"
    )

    file_location = models.TextField(null=False)

    score = models.IntegerField(default=0, null=False)
    feedback = models.TextField(default="", null=False)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class PythonTestSubmissionsException(Exception):
    detail = "python test submission error"


class PythonTestSubmissionsClosedException(PythonTestSubmissionsException):
    detail = "python test submission closed"


class PythonTestSubmissionsNotOpenException(PythonTestSubmissionsException):
    detail = "python test submission not open yet"


class Application(models.Model):
    user = models.OneToOneField("users.User", on_delete=models.CASCADE)

    # python test
    _python_test_duration = timedelta(hours=2)
    _python_test_real_duration = timedelta(hours=2, minutes=3)
    _python_test_passed_score = 75

    python_test_downloaded_at = models.DateTimeField(null=True, default=None)

    @property
    def _python_test_submission_closes_at(self) -> Optional[datetime]:
        if self.python_test_downloaded_at is None:
            return None
        return self.python_test_downloaded_at + self._python_test_real_duration

    def _python_test_raise_if_submission_not_open(self) -> None:
        if self._python_test_submission_closes_at is None:
            raise PythonTestSubmissionsNotOpenException
        if self._python_test_submission_closes_at < datetime.now():
            raise PythonTestSubmissionsClosedException

    @property
    def python_test_submission_is_open(self) -> bool:
        try:
            self._python_test_raise_if_submission_not_open()
        except PythonTestSubmissionsException:
            return False
        return True

    @property
    def python_test_status(self) -> str:
        if self.python_test_downloaded_at is None:
            return "to do"
        if self.python_test_submission_is_open:
            return "ongoing"
        return "finished"

    def new_python_test_submission(self, submission: PythonTestSubmission) -> None:
        try:
            self._python_test_raise_if_submission_not_open()
        except PythonTestSubmissionsException as e:
            logger.info(f"application_id={self.id}: unsuccessful submission ({e.detail}")
            raise e

        logger.info(f"application_id={self.id}: successful submission")
        submission.application = self
        submission.save()

    @property
    def python_test_best_score(self) -> Optional[int]:
        return PythonTestSubmission.objects.filter(application=self).aggregate(models.Max("score"))["score__max"]

    @property
    def python_test_passed(self) -> bool:
        return (
            self.python_test_best_score is not None and self.python_test_best_score >= self._python_test_passed_score
        )

    # slu-1

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

from datetime import datetime, timedelta
from logging import getLogger
from typing import Optional

from django.db import models

logger = getLogger(__name__)


class CodingTestSubmission(models.Model):
    application = models.ForeignKey(
        to="applications.Application", on_delete=models.CASCADE, related_name="coding_tests"
    )

    file_location = models.TextField(null=False)

    score = models.IntegerField(default=0, null=False)
    feedback = models.TextField(default="", null=False)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class CodingTestSubmissionsException(Exception):
    detail = "coding test submission error"


class CodingTestSubmissionsClosedException(CodingTestSubmissionsException):
    detail = "coding test submission closed"


class CodingTestSubmissionsNotOpenException(CodingTestSubmissionsException):
    detail = "coding test submission not open yet"


class Application(models.Model):
    user = models.OneToOneField("users.User", on_delete=models.CASCADE)

    # coding test
    _coding_test_duration = timedelta(hours=2)
    _coding_test_real_duration = timedelta(hours=2, minutes=3)
    _coding_test_passed_score = 75

    coding_test_downloaded_at = models.DateTimeField(null=True, default=None)

    @property
    def coding_test_submission_closes_at(self) -> Optional[datetime]:
        if self.coding_test_downloaded_at is None:
            return None
        return self.coding_test_downloaded_at + self._coding_test_real_duration

    def _coding_test_raise_if_submission_not_open(self) -> None:
        if self.coding_test_submission_closes_at is None:
            raise CodingTestSubmissionsNotOpenException
        if self.coding_test_submission_closes_at < datetime.now():
            raise CodingTestSubmissionsClosedException

    @property
    def coding_test_submission_is_open(self) -> bool:
        try:
            self._coding_test_raise_if_submission_not_open()
        except CodingTestSubmissionsException:
            return False
        return True

    @property
    def coding_test_status(self) -> str:
        if self.coding_test_downloaded_at is None:
            return "to do"
        if self.coding_test_submission_is_open:
            return "ongoing"
        return "finished"

    def new_coding_test_submission(self, submission: CodingTestSubmission) -> None:
        try:
            self._coding_test_raise_if_submission_not_open()
        except CodingTestSubmissionsException as e:
            logger.info(f"application_id={self.id}: unsuccessful submission ({e.detail}")
            raise e

        logger.info(f"application_id={self.id}: successful submission")
        submission.application = self
        submission.save()

    @property
    def coding_test_best_score(self) -> Optional[int]:
        return CodingTestSubmission.objects.filter(application=self).aggregate(models.Max("score"))["score__max"]

    @property
    def coding_test_passed(self) -> bool:
        return (
            self.coding_test_best_score is not None and self.coding_test_best_score >= self._coding_test_passed_score
        )

    # slu-1

    # slu-2

    # slu-3

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

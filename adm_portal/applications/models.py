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
    pass


class PythonTestSubmissionsClosedException(PythonTestSubmissionsException):
    pass


class PythonTestSubmissionsNotOpenException(PythonTestSubmissionsException):
    pass


class Application(models.Model):
    user = models.OneToOneField("users.User", on_delete=models.CASCADE)

    python_test_duration = timedelta(hours=2)
    python_test_real_duration = timedelta(hours=2, minutes=3)

    python_test_downloaded_at = models.DateTimeField(null=True, default=None)

    @property
    def python_test_submission_closes_at(self) -> Optional[datetime]:
        if self.python_test_downloaded_at is None:
            return None
        return self.python_test_downloaded_at + self.python_test_real_duration

    def new_python_test_submission(self, submission: PythonTestSubmission) -> None:
        if self.python_test_submission_closes_at is None:
            logger.info(f"application_id={self.id}: unsuccessful submission - not open error")
            raise PythonTestSubmissionsNotOpenException
        if self.python_test_submission_closes_at < datetime.now():
            logger.info(f"application_id={self.id}: unsuccessful submission - closed error")
            raise PythonTestSubmissionsClosedException

        logger.info(f"application_id={self.id}: successful submission")
        submission.application = self
        submission.save()

    @property
    def best_python_test_score(self) -> Optional[int]:
        return PythonTestSubmission.objects.filter(application=self).aggregate(models.Max("score"))["score__max"]

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

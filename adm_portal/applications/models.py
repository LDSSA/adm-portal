from datetime import datetime, timedelta
from logging import getLogger
from typing import NamedTuple, Optional

from django.db import models

logger = getLogger(__name__)


class SubmissionTypeStaticInfo(NamedTuple):
    uname: str
    max_score: int
    pass_score: int
    repo: Optional[str]


class SubmissionTypes:
    coding_test = SubmissionTypeStaticInfo(uname="coding_test", max_score=100, pass_score=75, repo=None)
    slu01 = SubmissionTypeStaticInfo(
        uname="slu01", max_score=100, pass_score=75, repo="https://github.com/Chi-Acci/adm-portal"
    )
    slu02 = SubmissionTypeStaticInfo(
        uname="slu02", max_score=100, pass_score=75, repo="https://github.com/Chi-Acci/adm-portal"
    )
    slu03 = SubmissionTypeStaticInfo(
        uname="slu03", max_score=100, pass_score=75, repo="https://github.com/Chi-Acci/adm-portal"
    )


class Submission(models.Model):
    application = models.ForeignKey(
        to="applications.Application", on_delete=models.CASCADE, related_name="submissions"
    )

    submission_type = models.CharField(null=False, max_length=20)

    file_location = models.TextField(null=False)

    score = models.IntegerField(default=0, null=False)
    feedback_location = models.TextField(null=False)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class SubmissionsException(Exception):
    detail = "submission error"


class SubmissionsClosedException(SubmissionsException):
    detail = "submission error (closed)"


class SubmissionsNotOpenException(SubmissionsException):
    detail = "submission error (not open yet)"


class Application(models.Model):
    user = models.OneToOneField("users.User", on_delete=models.CASCADE)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # submission types #####################################################

    # coding test ##########################################################
    _coding_test_duration = timedelta(hours=2)
    _coding_test_real_duration = timedelta(hours=2, minutes=3)
    _coding_test_passed_score = 75

    coding_test_started_at = models.DateTimeField(null=True, default=None)

    @property
    def coding_test_submission_closes_at(self) -> Optional[datetime]:
        if self.coding_test_started_at is None:
            return None
        return self.coding_test_started_at + self._coding_test_real_duration

    def _coding_test_raise_if_submission_not_open(self) -> None:
        if self.coding_test_submission_closes_at is None:
            raise SubmissionsNotOpenException
        if self.coding_test_submission_closes_at < datetime.now():
            raise SubmissionsClosedException

    @property
    def coding_test_submission_is_open(self) -> bool:
        try:
            self._coding_test_raise_if_submission_not_open()
        except SubmissionsException:
            return False
        return True

    def coding_test_new_submission(self, submission: Submission) -> None:
        try:
            submission.submission_type = SubmissionTypes.coding_test.uname
            self._coding_test_raise_if_submission_not_open()
        except SubmissionsException as e:
            logger.info(f"application_id={self.id}: unsuccessful submission ({e.detail}")
            raise e

        logger.info(f"application_id={self.id}: successful submission")
        submission.application = self
        submission.save()

    @property
    def coding_test_status(self) -> str:
        if self.coding_test_started_at is None:
            return "to do"
        if self.coding_test_submission_is_open:
            return "ongoing"
        return "finished"

    @property
    def coding_test_best_score(self) -> Optional[int]:
        return self.query_best_score(submission_type=SubmissionTypes.coding_test)

    @property
    def coding_test_passed(self) -> bool:
        return self.query_passed(submission_type=SubmissionTypes.coding_test)

    @property
    def slu01_best_score(self) -> Optional[int]:
        return self.query_best_score(submission_type=SubmissionTypes.slu01)

    @property
    def slu01_passed(self) -> bool:
        return self.query_passed(submission_type=SubmissionTypes.slu01)

    @property
    def slu02_best_score(self) -> Optional[int]:
        return self.query_best_score(submission_type=SubmissionTypes.slu02)

    @property
    def slu02_passed(self) -> bool:
        return self.query_passed(submission_type=SubmissionTypes.slu02)

    @property
    def slu03_best_score(self) -> Optional[int]:
        return self.query_best_score(submission_type=SubmissionTypes.slu03)

    @property
    def slu03_passed(self) -> bool:
        return self.query_passed(submission_type=SubmissionTypes.slu03)

    @property
    def passed(self) -> bool:
        return self.coding_test_passed and self.slu01_passed and self.slu02_passed and self.slu03_passed

    def query_best_score(self, submission_type: SubmissionTypeStaticInfo) -> Optional[int]:
        return Submission.objects.filter(application=self, submission_type=submission_type.uname).aggregate(
            models.Max("score")
        )["score__max"]

    def query_passed(self, submission_type: SubmissionTypeStaticInfo) -> bool:
        best_score = self.query_best_score(submission_type)
        return best_score is not None and best_score >= submission_type.pass_score

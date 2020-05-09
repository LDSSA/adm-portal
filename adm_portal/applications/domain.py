from datetime import datetime, timedelta
from enum import Enum
from logging import getLogger
from typing import Dict, Optional

from django.db import models

from interface import interface

from .models import Application, Submission, SubmissionType, SubmissionTypes

logger = getLogger(__name__)


class Status(Enum):
    not_started = "Not Started"
    ongoing = "On Going"
    passed = "Passed"
    failed = "Failed"


ApplicationStatus = Status
SubmissionStatus = Status


class Domain:
    # a candidate is only allowed to get graded MAX_SUBMISSIONS of times per submission type
    max_submissions = 250

    @staticmethod
    def get_application_status(application: Application) -> ApplicationStatus:
        return Domain.get_application_detailed_status(application)["application"]

    @staticmethod
    def get_application_detailed_status(application: Application) -> Dict[str, Status]:
        sub_type_status = {}
        for sub_type in SubmissionTypes.all:
            sub_type_status[sub_type.uname] = Domain.get_sub_type_status(application, sub_type)

        application_status = None
        if any((s == SubmissionStatus.failed for _, s in sub_type_status.items())):
            application_status = ApplicationStatus.failed
        elif any((s == SubmissionStatus.ongoing for _, s in sub_type_status.items())):
            application_status = ApplicationStatus.ongoing
        elif all((s == SubmissionStatus.passed for _, s in sub_type_status.items())):
            application_status = ApplicationStatus.passed
        elif all((s == SubmissionStatus.not_started for _, s in sub_type_status.items())):
            application_status = ApplicationStatus.not_started
        else:
            # some tests passed, some not started
            application_status = ApplicationStatus.ongoing

        return {"application": application_status, **sub_type_status}

    @staticmethod
    def get_sub_type_status(application: Application, sub_type: SubmissionType) -> SubmissionStatus:
        if Domain.has_positive_score(application, sub_type):
            return SubmissionStatus.passed
        if Domain.get_start_date(application, sub_type) is None:
            return SubmissionStatus.not_started
        if datetime.now() < Domain.get_close_date(application, sub_type):
            return SubmissionStatus.ongoing
        return SubmissionStatus.failed

    @staticmethod
    def get_start_date(application: Application, sub_type: SubmissionType) -> Optional[datetime]:
        start_date = getattr(application, f"{sub_type.uname}_started_at", None)
        return start_date

    @staticmethod
    def get_close_date(application: Application, sub_type: SubmissionType, *, apply_buffer: bool = False) -> datetime:
        start_date = Domain.get_start_date(application, sub_type)
        if start_date is None:
            raise DomainException("Cant compute `close_date` with null `start_date`")
        if apply_buffer:
            # buffer is applied to account for possible latency (lambda grader func may take a while)
            return start_date + sub_type.duration + Domain.submission_timedelta_buffer
        else:
            return start_date + sub_type.duration

    @staticmethod
    def get_best_score(application: Application, sub_type: SubmissionType) -> Optional[int]:
        return Submission.objects.filter(application=application, submission_type=sub_type.uname).aggregate(
            models.Max("score")
        )["score__max"]

    @staticmethod
    def has_positive_score(application: Application, sub_type: SubmissionType) -> bool:
        score = Domain.get_best_score(application, sub_type)
        return score is not None and score >= sub_type.pass_score

    @staticmethod
    def can_add_submission(application: Application, sub_type: SubmissionType) -> bool:
        if Domain.get_start_date(application, sub_type) is None:
            return False

        if datetime.now() > Domain.get_close_date(application, sub_type, apply_buffer=True):
            return False

        if not interface.feature_flag_client.applications_are_open():
            return False

        if (
            Submission.objects.filter(application=application, submission_type=sub_type.uname).count()
            >= Domain.max_submissions
        ):
            logger.warning(f"user `{application.user.email}` reached max submissions.")
            return False

        return True

    @staticmethod
    def add_submission(application: Application, sub_type: SubmissionType, sub: Submission) -> None:
        if not Domain.can_add_submission(application, sub_type):
            raise DomainException("Can't add submission")

        sub.application = application
        sub.submission_type = sub_type.uname
        sub.save()

    # constants
    submission_timedelta_buffer = timedelta(minutes=2)


class DomainException(Exception):
    pass

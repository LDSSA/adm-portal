import random
from abc import ABC, abstractmethod
from logging import getLogger
from typing import NamedTuple

import requests

logger = getLogger(__name__)


class SubmissionResult(NamedTuple):
    score: int
    max_score: int
    feedback_s3_bucket: str
    feedback_s3_key: str


class GraderClientException(Exception):
    pass


class GraderClient(ABC):
    @abstractmethod
    def grade(
        self, assignment_id: str, user_uuid: str, submission_s3_bucket: str, submission_s3_key: str
    ) -> SubmissionResult:
        pass


class GraderClientHttp(GraderClient):
    def __init__(self, url: str, auth_token: str) -> None:
        self.url = url
        self.auth_token = auth_token

    def grade(
        self, assignment_id: str, user_uuid: str, submission_s3_bucket: str, submission_s3_key: str
    ) -> SubmissionResult:
        url = self.url
        headers = {"Authorization": f"{self.auth_token}", "Content-Type": "application/json"}
        body = {
            "assignmentID": assignment_id,
            "userUUID": user_uuid,
            "submissionS3Bucket": submission_s3_bucket,
            "submissionS3Key": submission_s3_key,
        }

        logger.info(f"grade request: url={url}, body={body}, authorization={self.auth_token[0:3]}***")

        r: requests.Response = requests.post(url=url, headers=headers, json=body)
        if not r.ok:
            raise GraderClientException(f"response status error: {r.status_code} ({r.json()})")

        try:
            data = r.json()
            logger.info(f"grade response: status_code={r.status_code}, data={data}")
            return SubmissionResult(
                score=data["score"],
                max_score=data["maxScore"],
                feedback_s3_bucket=data["feedbackS3Bucket"],
                feedback_s3_key=data["feedbackS3Key"],
            )
        except KeyError as e:
            raise GraderClientException(f"response payload error: ({str(e)}")


class GraderClientFakeScores(GraderClient):
    def grade(
        self, assignment_id: str, user_uuid: str, submission_s3_bucket: str, submission_s3_key: str
    ) -> SubmissionResult:
        return SubmissionResult(
            score=random.randrange(10, 20, 2),
            max_score=20,
            feedback_s3_bucket=submission_s3_bucket,
            feedback_s3_key="coding-test-feedback/example_feedback.html",
        )

from typing import Optional

from django.conf import settings

from feature_flags_client import FeatureFlagsClient, InCodeFeatureFlagsClient
from grander_client import GraderClient, GraderClientFakeScores, GraderClientHttp
from storage_client import AWSS3StorageClient, LocalStorageClient, StorageClient


class InterfaceException(Exception):
    def __init__(self, msg: str) -> None:
        self.msg = msg

    def __str__(self) -> str:
        return self.msg


def get_storage_client(storage_client_type: Optional[str] = None) -> StorageClient:
    storage_client_type = storage_client_type or settings.STORAGE_CLIENT
    if storage_client_type == "S3":
        return AWSS3StorageClient(bucket_name=settings.STORAGE_CLIENT_NAMESPACE)
    elif storage_client_type == "LOCAL":
        return LocalStorageClient(workspace=settings.STORAGE_CLIENT_NAMESPACE)
    raise InterfaceException(msg=f"No StorageClient implementation for `{storage_client_type}`")


def get_feature_flag_client(ff_client_type: Optional[str] = None) -> FeatureFlagsClient:
    ff_client_type = ff_client_type or settings.FF_CLIENT
    if ff_client_type == "CODE":
        return InCodeFeatureFlagsClient()
    raise InterfaceException(msg=f"No FeatureFlagsClient implementation for `{ff_client_type}`")


def get_grader_client(grader_client_type: Optional[str] = None) -> GraderClient:
    grader_client_type = grader_client_type or settings.GRADER_CLIENT
    if grader_client_type == "HTTP":
        return GraderClientHttp(url=settings.GRADER_CLIENT_URL, auth_token=settings.GRADER_CLIENT_AUTH_TOKE)
    if grader_client_type == "FAKE":
        return GraderClientFakeScores()
    raise InterfaceException(msg=f"No GraderClient implementation for `{grader_client_type}`")

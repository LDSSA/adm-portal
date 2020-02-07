from django.conf import settings

from storage_client import AWSS3StorageClient, LocalStorageClient, StorageClient


class InterfaceException(Exception):
    def __init__(self, msg: str) -> None:
        self.msg = msg

    def __str__(self) -> str:
        return self.msg


def get_storage_client() -> StorageClient:
    if settings.STORAGE_CLIENT == "S3":
        return AWSS3StorageClient(bucket_name=settings.STORAGE_CLIENT_NAMESPACE)
    elif settings.STORAGE_CLIENT == "LOCAL":
        return LocalStorageClient(workspace=settings.STORAGE_CLIENT_NAMESPACE)
    raise InterfaceException(msg=f"No StorageClient implementation for `{settings.STORAGE_CLIENT}`")

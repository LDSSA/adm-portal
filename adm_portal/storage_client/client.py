import logging
from abc import ABC, abstractmethod
from typing import Any

import boto3
from boto3.exceptions import Boto3Error

logger = logging.getLogger(__name__)


class StorageClientException(Exception):
    def __init__(self, e: Exception) -> None:
        self.e = e

    def __str__(self) -> str:
        return str(self.e)


class StorageClient(ABC):
    @abstractmethod
    def save(self, key: str, file: Any) -> None:
        pass


class AWSS3StorageClient(StorageClient):
    def __init__(self, bucket_name: str) -> None:
        self.bucket_name = bucket_name

    def save(self, key: str, file: Any) -> None:
        s3 = boto3.resource("s3")
        try:
            s3_obj = s3.Bucket(self.bucket_name).put_object(Key=key, Body=file)
            logger.info(f"s3 upload success: {s3_obj.bucket_name}/{s3_obj.key}")
        except Boto3Error as e:
            logger.info(f"s3 upload error: {e}")
            raise StorageClientException(e)


class LocalStorageClient(StorageClient):
    def __init__(self, workspace: str) -> None:
        self.workspace = workspace

    def save(self, key: str, file: Any) -> None:
        try:
            with open(f"{self.workspace}/{key}", "wb+") as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
        except StorageClientException as e:
            raise StorageClientException(e)

import logging
from typing import Any, Optional

import boto3
from boto3.exceptions import Boto3Error

from .client import StorageClient, StorageClientException

logger = logging.getLogger(__name__)


class AWSS3StorageClient(StorageClient):
    def __init__(self, bucket_name: str) -> None:
        self.bucket_name = bucket_name

    def save(self, key: str, file: Any) -> None:
        s3 = boto3.resource("s3")
        try:
            s3_obj = s3.Bucket(self.bucket_name).put_object(Key=key, Body=file)
            logger.info(f"s3 upload success: {s3_obj.bucket_name}/{s3_obj.key}")
        except Boto3Error as e:
            logger.error(f"s3 upload error: {e}")
            raise StorageClientException(e)

    def get_url(self, key: str, *, content_type: Optional[str] = None) -> str:
        params = {"Bucket": self.bucket_name, "Key": key}
        if content_type is not None:
            params["ResponseContentType"] = content_type
        try:
            return boto3.client("s3").generate_presigned_url(ClientMethod="get_object", Params=params, ExpiresIn=30)
        except Boto3Error as e:
            logger.error(f"s3 url gen error: {e}")
            raise StorageClientException(e)

    def get_attachment_url(self, key: str, *, content_type: Optional[str] = None) -> str:
        content_type = content_type or "application/octet-stream"
        try:
            return boto3.client("s3").generate_presigned_url(
                ClientMethod="get_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": key,
                    "ResponseContentDisposition": f"attachment; filename={key}",
                    "ResponseContentType": content_type,
                },
                ExpiresIn=30,
            )
        except Boto3Error as e:
            logger.error(f"s3 url gen error: {e}")
            raise e

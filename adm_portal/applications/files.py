from datetime import datetime
from logging import getLogger
from typing import Any

import boto3
from botocore.exceptions import ClientError

from interface import get_storage_client
from users.models import UserData

logger = getLogger(__name__)


# todo: use get_storage_client or leave this hardcoded from s3 ?
def get_coding_test_url_from_s3(bucket: str) -> str:
    key = "ldssa_coding_test_2020.ipynb"
    try:
        return boto3.client("s3").generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": bucket,
                "Key": key,
                "ResponseContentDisposition": f"attachment; filename={key}",
                "ResponseContentType": "application/vnd.jupyter",
            },
            ExpiresIn=30,
        )
    except ClientError as e:
        logger.error(e)
        raise e


def upload_coding_test_solution(u: UserData, file: Any) -> str:
    base = "coding-test-submissions"
    now_str = datetime.now().strftime("%m_%d_%Y__%H_%M_%S")
    key = f"{base}/{u.uuid}/{file.name}@{now_str}"

    get_storage_client().save(key, file)
    return key

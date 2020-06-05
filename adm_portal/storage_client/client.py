import os
import uuid
from abc import ABC, abstractmethod
from typing import Any, Optional


class StorageClientException(Exception):
    def __init__(self, e: Exception) -> None:
        self.e = e

    def __str__(self) -> str:
        return str(self.e)


class StorageClient(ABC):
    @staticmethod
    def key_append_uuid(key: str) -> str:
        key_basename, key_ext = os.path.splitext(key)
        return f"{key_basename}_{uuid.uuid4().hex}{key_ext}"

    @abstractmethod
    def save(self, key: str, file: Any) -> None:
        pass

    @abstractmethod
    def get_url(self, key: str, *, content_type: Optional[str] = None) -> str:
        pass

    @abstractmethod
    def get_attachment_url(
        self, key: str, *, content_type: Optional[str] = None, filename: Optional[str] = None
    ) -> str:
        pass

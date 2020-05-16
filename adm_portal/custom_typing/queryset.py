from typing import Generic, Iterator, TypeVar

from django.db.models import QuerySet as ModelQuerySet

_Z = TypeVar("_Z")


class QuerySet(Generic[_Z], ModelQuerySet):
    def __iter__(self) -> Iterator[_Z]:
        ...

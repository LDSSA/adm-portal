from feature_flags_client.db import GetSetFlagsInterface

from .models import Flags


class FlagsGetSet(GetSetFlagsInterface):
    def set(self, *, key: str, value: str, create_by: str = "") -> None:
        Flags.objects.create(key=key, value=value, created_by=create_by)

    def get(self, *, key: str) -> str:
        try:
            return Flags.objects.filter(key=key).latest().value
        except Flags.DoesNotExist:
            return ""

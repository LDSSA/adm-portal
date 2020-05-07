from django.test import TestCase

from staff.domain import FlagsGetSet
from staff.models import Flags

flags = FlagsGetSet()


class TestFlagsGetSet(TestCase):
    def test_get_empty(self) -> None:
        value = flags.get(key="notfound")
        self.assertEqual(value, "")

    def test_get(self) -> None:
        Flags.objects.create(key="key", value="value-j", created_by="joao@adm.com")
        Flags.objects.create(key="key", value="value-m", created_by="maria@adm.com")

        value = flags.get(key="key")
        self.assertEqual(value, "value-m")

    def test_set(self) -> None:
        flags.set(key="key", value="value1", create_by="joao@adm.com")
        self.assertEqual(Flags.objects.count(), 1)
        self.assertEqual(Flags.objects.latest().key, "key")
        self.assertEqual(Flags.objects.latest().value, "value1")
        self.assertEqual(Flags.objects.latest().created_by, "joao@adm.com")

        flags.set(key="key", value="value2", create_by="joao@adm.com")
        self.assertEqual(Flags.objects.count(), 2)
        self.assertEqual(Flags.objects.latest().key, "key")
        self.assertEqual(Flags.objects.latest().value, "value2")
        self.assertEqual(Flags.objects.latest().created_by, "joao@adm.com")

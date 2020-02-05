from django.contrib.auth import authenticate
from django.test import TestCase

from users.models import User


class TestUserBackend(TestCase):
    def setUp(self) -> None:
        User.objects.create_user(email="chi@adm.com", password="pw")

    def test_none_fail(self) -> None:
        self.assertIsNone(authenticate())

    def test_authenticate_no_password(self) -> None:
        self.assertIsNone(authenticate(email="chi@adm.com"))

    def test_authenticate_bad_password(self) -> None:
        self.assertIsNone(authenticate(email="chi@adm.com", password="bad_pw"))

    def test_authenticate_success(self) -> None:
        self.assertIsNotNone(authenticate(email="chi@adm.com", password="pw"))

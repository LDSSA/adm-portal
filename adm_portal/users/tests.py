from django.contrib.auth import authenticate
from django.test import TestCase

from .models import User

USER_CHI = {"email": "chi@adm.com", "password": "verystrong1"}

USER_JOAO = {"email": "joao@adm.com", "password": "verystrong2"}


class TestUserBackend(TestCase):
    def setUp(self) -> None:
        User.objects.create_user(**USER_CHI)
        User.objects.create_user(**USER_JOAO)

    def test_none_fail(self) -> None:
        self.assertIsNone(authenticate())

    def test_no_user_fail(self) -> None:
        self.assertIsNone(authenticate(email="bad_username"))

    def test_email_authentication_fail(self) -> None:
        self.assertIsNone(authenticate(email=USER_CHI["email"], password=USER_JOAO["password"]))

    def test_email_authentication_success(self) -> None:
        self.assertIsNotNone(authenticate(email=USER_CHI["email"], password=USER_CHI["password"]))


class TestUserManager(TestCase):
    def test_create_user_success(self) -> None:
        self.assertEqual(User.objects.count(), 0)
        user = User.objects.create_user(**USER_JOAO)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(user.email, USER_JOAO["email"])
        self.assertTrue(user.check_password(USER_JOAO["password"]))

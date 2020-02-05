from django.test import TestCase

from users.models import User


class TestUserManager(TestCase):
    def test_create_user_success(self) -> None:
        self.assertEqual(User.objects.count(), 0)
        user = User.objects.create_user(email="joao@adm.com", password="verystrong")
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(user.email, "joao@adm.com")
        self.assertTrue(user.check_password("verystrong"))
        self.assertFalse(user.check_password("notverystrong"))

from django.test import TestCase

from users.models import User, UserConfirmEmail


class TestUserManager(TestCase):
    def test_create_user_defaults(self) -> None:
        u = User.objects.create_user(email="joao@adm.com", password="verystrong")
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(u.email, "joao@adm.com")
        self.assertTrue(u.check_password("verystrong"))
        self.assertFalse(u.check_password("notverystrong"))
        self.assertFalse(u.is_staff)
        self.assertFalse(u.email_confirmed)
        self.assertEqual(UserConfirmEmail.objects.count(), 1)
        self.assertEqual(UserConfirmEmail.objects.filter(user=u).count(), 1)

    def test_create_staff_user_defaults(self) -> None:
        u = User.objects.create_staff_user(email="joao@adm.com", password="verystrong")
        self.assertEqual(u.email, "joao@adm.com")
        self.assertTrue(u.check_password("verystrong"))
        self.assertFalse(u.check_password("notverystrong"))
        self.assertTrue(u.is_staff)
        self.assertTrue(u.email_confirmed)
        self.assertEqual(UserConfirmEmail.objects.count(), 0)

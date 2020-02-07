from django.contrib import auth
from django.db import transaction
from django.test import Client, TestCase

from users.models import User


class TestUserSignupViews(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(email="joao@protonmail.com", password="joao_pw")
        self.staff_user = User.objects.create_staff_user(email="chi@adm.com", password="chi_pw")

    def test_get_signup_success_200(self) -> None:
        response = Client().get("/account/signup")
        self.assertEqual(response.status_code, 200)

    def test_get_signup_success_302(self) -> None:
        client = Client()
        client.login(email=self.user.email, password="joao_pw")
        response = client.get("/account/signup")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/candidate/home")

        self.assertTrue(assert_logged_as(client, self.user))

    def test_get_signup_success_302_staff(self) -> None:
        client = Client()
        client.login(email=self.staff_user.email, password="chi_pw")
        response = client.get("/account/signup")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/staff/home")

        self.assertTrue(assert_logged_as(client, self.staff_user))

    def test_post_signup_success_302(self) -> None:
        client = Client()
        response = client.post("/account/signup", {"email": "vasco@sf.com", "password": "vasco_pw"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/candidate/home")
        new_user = User.objects.get(email="vasco@sf.com")
        self.assertTrue(new_user.check_password("vasco_pw"))

        self.assertTrue(assert_logged_as(client, new_user))
        self.assertFalse(new_user.is_staff)

    def test_post_signup_email_error_409(self) -> None:
        with transaction.atomic():
            response = Client().post("/account/signup", {"email": "joao@protonmail.com", "password": "pw"})
        self.assertEqual(response.status_code, 409)
        self.assertFalse(auth.get_user(self.client).is_authenticated)

    def test_post_signup_email_error_409_staff(self) -> None:
        with transaction.atomic():
            response = Client().post("/account/signup", {"email": "chi@adm.com", "password": "pw"})
        self.assertEqual(response.status_code, 409)
        self.assertFalse(auth.get_user(self.client).is_authenticated)


class TestUserLoginViews(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(email="joao@protonmail.com", password="joao_pw")
        self.staff_user = User.objects.create_staff_user(email="chi@adm.com", password="chi_pw")

    def test_get_login_success_200(self) -> None:
        response = Client().get("/account/login")
        self.assertEqual(response.status_code, 200)

    def test_get_login_success_302(self) -> None:
        client = Client()
        client.login(email=self.user.email, password="joao_pw")
        response = client.get("/account/login")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/candidate/home")

        self.assertTrue(assert_logged_as(client, self.user))

    def test_get_login_success_302_staff(self) -> None:
        client = Client()
        client.login(email=self.staff_user.email, password="chi_pw")
        response = client.get("/account/login")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/staff/home")

        self.assertTrue(assert_logged_as(client, self.staff_user))

    def test_post_login_success_302(self) -> None:
        client = Client()
        response = client.post("/account/login", {"email": "joao@protonmail.com", "password": "joao_pw"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/candidate/home")

        self.assertTrue(assert_logged_as(client, self.user))

    def test_post_login_success_302_staff(self) -> None:
        client = Client()
        response = client.post("/account/login", {"email": "chi@adm.com", "password": "chi_pw"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/staff/home")

        self.assertTrue(assert_logged_as(client, self.staff_user))

    def test_post_login_email_error_400(self) -> None:
        response = Client().post("/account/login", {"email": "vasco@o.com", "password": "joao_pw"})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(auth.get_user(self.client).is_authenticated)

    def test_post_login_password_error_400(self) -> None:
        response = Client().post("/account/login", {"email": "joao@protonmail.com", "password": "vasco_pw"})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(auth.get_user(self.client).is_authenticated)


class TestUserLogoutViews(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(email="joao@protonmail.com", password="joao_pw")
        self.staff_user = User.objects.create_staff_user(email="chi@adm.com", password="chi_pw")

    def test_post_logout_success_302(self) -> None:
        client = Client()
        client.login(email=self.user.email, password="joao_pw")
        response = Client().get("/account/logout")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/account/login")

    def test_post_logout_success_302_staff(self) -> None:
        client = Client()
        client.login(email=self.staff_user.email, password="chi_pw")
        response = Client().get("/account/logout")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/account/login")


def assert_logged_as(client: Client, user: User) -> bool:
    logged_user = auth.get_user(client)
    return logged_user.is_authenticated and user == logged_user

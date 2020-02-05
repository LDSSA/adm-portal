from django.contrib import auth
from django.db import transaction
from django.test import Client, TestCase

from users.models import User


class TestUserSignupViews(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(email="chi@adm.com", password="chi_pw")

    def test_get_signup_success_200(self) -> None:
        response = Client().get("/users/signup")
        self.assertEqual(response.status_code, 200)

    def test_get_signup_success_302(self) -> None:
        client = Client()
        client.login(email=self.user.email, password="chi_pw")
        response = client.get("/users/signup")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")

        self.assertTrue(assert_logged_as(client, self.user))

    def test_post_signup_success_302(self) -> None:
        client = Client()
        response = client.post("/users/signup", {"email": "joao@adm.com", "password": "pw"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")
        new_user = User.objects.get(email="joao@adm.com")
        self.assertTrue(new_user.check_password("pw"))

        self.assertTrue(assert_logged_as(client, new_user))

    def test_post_signup_email_error_409(self) -> None:
        with transaction.atomic():
            response = Client().post("/users/signup", {"email": "chi@adm.com", "password": "pw"})
        self.assertEqual(response.status_code, 409)
        self.assertFalse(auth.get_user(self.client).is_authenticated)


class TestUserLoginViews(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(email="chi@adm.com", password="chi_pw")

    def test_get_login_success_200(self) -> None:
        response = Client().get("/users/login")
        self.assertEqual(response.status_code, 200)

    def test_get_login_success_302(self) -> None:
        client = Client()
        client.login(email=self.user.email, password="chi_pw")
        response = client.get("/users/login")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")

        self.assertTrue(assert_logged_as(client, self.user))

    def test_post_login_success_302(self) -> None:
        client = Client()
        response = client.post("/users/login", {"email": "chi@adm.com", "password": "chi_pw"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")

        self.assertTrue(assert_logged_as(client, self.user))

    def test_post_login_email_error_400(self) -> None:
        response = Client().post("/users/login", {"email": "joao@adm.com", "password": "chi_pw"})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(auth.get_user(self.client).is_authenticated)

    def test_post_login_password_error_400(self) -> None:
        response = Client().post("/users/login", {"email": "chi@adm.com", "password": "joao_pw"})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(auth.get_user(self.client).is_authenticated)


class TestUserLogoutViews(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(email="chi@adm.com", password="chi_pw")

    def test_post_logout_success_302(self) -> None:
        client = Client()
        client.login(email=self.user.email, password="chi_pw")
        response = Client().get("/users/logout")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/users/login")


def assert_logged_as(client: Client, user: User) -> bool:
    logged_user = auth.get_user(client)
    return logged_user.is_authenticated and user == logged_user

from django.contrib import auth
from django.db import transaction
from django.test import Client, TestCase

from interface import interface
from users.models import User, UserConfirmEmail, UserResetPassword


class TestUserSignupViews(TestCase):
    def setUp(self) -> None:
        interface.feature_flag_client.open_signups()
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

        self.assertTrue(is_logged_as(client, self.user))

    def test_get_signup_success_302_staff(self) -> None:
        client = Client()
        client.login(email=self.staff_user.email, password="chi_pw")
        response = client.get("/account/signup")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/staff/home")

        self.assertTrue(is_logged_as(client, self.staff_user))

    def test_post_signup_success_302(self) -> None:
        # todo: assert confirm email sent
        client = Client()
        response = client.post("/account/signup", {"email": "vasco@sf.com", "password": "vasco_pw"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/candidate/home")
        new_user = User.objects.get(email="vasco@sf.com")
        self.assertTrue(new_user.check_password("vasco_pw"))

        self.assertTrue(is_logged_as(client, new_user))
        self.assertFalse(new_user.is_staff)

    def test_post_signup_email_error_409(self) -> None:
        # todo: assert confirm email NOT sent
        with transaction.atomic():
            response = Client().post("/account/signup", {"email": "joao@protonmail.com", "password": "pw"})
        self.assertEqual(response.status_code, 409)
        self.assertFalse(auth.get_user(self.client).is_authenticated)

    def test_post_signup_email_error_409_staff(self) -> None:
        # todo: assert confirm email NOT sent
        with transaction.atomic():
            response = Client().post("/account/signup", {"email": "chi@adm.com", "password": "pw"})
        self.assertEqual(response.status_code, 409)
        self.assertFalse(auth.get_user(self.client).is_authenticated)

    def test_get_signup_closed_400(self) -> None:
        interface.feature_flag_client.close_signups()
        response = Client().get("/account/signup")
        self.assertEqual(response.status_code, 400)

    def test_post_signup_closed_302(self) -> None:
        interface.feature_flag_client.close_signups()
        client = Client()
        response = client.post("/account/signup", {"email": "vasco@sf.com", "password": "vasco_pw"})
        self.assertEqual(response.status_code, 400)


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

        self.assertTrue(is_logged_as(client, self.user))

    def test_get_login_success_302_staff(self) -> None:
        client = Client()
        client.login(email=self.staff_user.email, password="chi_pw")
        response = client.get("/account/login")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/staff/home")

        self.assertTrue(is_logged_as(client, self.staff_user))

    def test_post_login_success_302(self) -> None:
        client = Client()
        response = client.post("/account/login", {"email": "joao@protonmail.com", "password": "joao_pw"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/candidate/home")

        self.assertTrue(is_logged_as(client, self.user))

    def test_post_login_success_302_staff(self) -> None:
        client = Client()
        response = client.post("/account/login", {"email": "chi@adm.com", "password": "chi_pw"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/staff/home")

        self.assertTrue(is_logged_as(client, self.staff_user))

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
        response = client.get("/account/logout")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/account/login")

    def test_post_logout_success_302_staff(self) -> None:
        client = Client()
        client.login(email=self.staff_user.email, password="chi_pw")
        response = Client().get("/account/logout")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/account/login")


class TestConfirmEmailViews(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(email="joao@protonmail.com", password="joao_pw")

    def test_get_confirm_email(self) -> None:
        token = UserConfirmEmail.objects.get(user=self.user).token
        client = Client()
        response = client.get("/account/confirm-email", {"token": token})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/candidate/home")
        self.assertEqual(UserConfirmEmail.objects.count(), 0)

        self.assertTrue(is_logged_as(client, self.user))

    def test_get_confirm_email_404_error(self) -> None:
        response = Client().get("/account/confirm-email", {"token": "token_doesnt_exist"})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(UserConfirmEmail.objects.filter(user=self.user).count(), 1)


class TestResetPasswordViews(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(email="joao@protonmail.com", password="joao_pw")

    def test_post_start_reset_password(self) -> None:
        # todo: assert email sent
        response = Client().post("/account/start-reset-password", {"email": "joao@protonmail.com"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(UserResetPassword.objects.filter(user=self.user).count(), 1)

    def test_post_start_reset_password_no_user(self) -> None:
        # todo: assert email NOT sent
        response = Client().post("/account/start-reset-password", {"email": "joao@protonmail.com"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(UserResetPassword.objects.filter(user=self.user).count(), 1)

    def test_get_reset_password(self) -> None:
        token = UserResetPassword.objects.create(user=self.user).token
        client = Client()
        response = client.get("/account/reset-password", {"token": token})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(UserConfirmEmail.objects.count(), 1)
        self.assertFalse(is_logged_as(client, self.user))

    def test_get_reset_password_404_error(self) -> None:
        client = Client()
        response = client.get("/account/reset-password", {"token": "token_doesnt_exist"})
        self.assertEqual(response.status_code, 404)
        self.assertFalse(is_logged_as(client, self.user))

    def test_post_reset_password(self) -> None:
        token = UserResetPassword.objects.create(user=self.user).token
        client = Client()
        response = client.post("/account/reset-password", {"token": token, "password": "my_new_password"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/candidate/home")
        self.assertEqual(UserResetPassword.objects.count(), 0)
        self.assertTrue(is_logged_as(client, self.user))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("my_new_password"))

    def test_post_reset_password_404_error(self) -> None:
        client = Client()
        response = client.post(
            "/account/reset-password", {"token": "token_doesnt_exist", "password": "my_new_password"}
        )
        self.assertEqual(response.status_code, 404)
        self.assertFalse(is_logged_as(client, self.user))
        self.assertFalse(self.user.check_password("my_new_password"))


class TestSendConfirmationEmailView(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(email="joao@protonmail.com", password="joao_pw")

    def test_get_success_302(self) -> None:
        client = Client()
        client.login(email=self.user.email, password="joao_pw")
        response = client.get("/account/send-confirmation-email")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/candidate/home")

    def test_get_error_302(self) -> None:
        response = Client().get("/account/logout")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/account/login")


def is_logged_as(client: Client, user: User) -> bool:
    logged_user = auth.get_user(client)
    return logged_user.is_authenticated and user == logged_user

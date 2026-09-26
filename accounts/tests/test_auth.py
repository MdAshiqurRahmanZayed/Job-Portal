from django.urls import reverse

from accounts.models import Account

from .base import TEST_FIXTURE_PASSWORD, AccountsTestCase


class RegistrationTests(AccountsTestCase):
    def test_valid_registration_creates_account(self):
        response = self.client.post(
            reverse("register"),
            {
                "email": "newuser@example.com",
                "password": TEST_FIXTURE_PASSWORD,
                "confirm_password": TEST_FIXTURE_PASSWORD,
            },
        )
        self.assertTrue(Account.objects.filter(email="newuser@example.com").exists())
        self.assertEqual(response.status_code, 302)

    def test_duplicate_email_is_rejected(self):
        self.make_account(email="dup@example.com")

        self.client.post(
            reverse("register"),
            {
                "email": "dup@example.com",
                "password": TEST_FIXTURE_PASSWORD,
                "confirm_password": TEST_FIXTURE_PASSWORD,
            },
        )

        self.assertEqual(Account.objects.filter(email="dup@example.com").count(), 1)


class LoginLogoutTests(AccountsTestCase):
    def setUp(self):
        self.account = self.make_account(
            email="login@example.com", password=TEST_FIXTURE_PASSWORD
        )

    def test_valid_credentials_log_in(self):
        response = self.client.post(
            reverse("login"),
            {"email": "login@example.com", "password": TEST_FIXTURE_PASSWORD},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("dashboard"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_invalid_credentials_are_rejected(self):
        response = self.client.post(
            reverse("login"),
            {"email": "login@example.com", "password": "WrongPassword"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_ends_session(self):
        self.login_as(self.account)
        self.assertIn("_auth_user_id", self.client.session)

        self.client.get(reverse("logout"))

        self.assertNotIn("_auth_user_id", self.client.session)

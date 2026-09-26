from django.urls import reverse

from apps.main.models import ConversationMessages

from .base import MainTestCase


class ChatMessageAPIViewTests(MainTestCase):
    def setUp(self):
        self.employer, self.employer_profile = self.make_account_with_profile(
            role="employer"
        )
        self.jobseeker, self.jobseeker_profile = self.make_account_with_profile(
            role="jobseeker"
        )
        self.job = self.make_job(self.employer_profile)
        self.application = self.make_application(self.job, self.jobseeker_profile)
        self.message = ConversationMessages.objects.create(
            application=self.application,
            content="Hello",
            created_by=self.jobseeker_profile,
        )

    def test_authenticated_get_returns_messages(self):
        self.login_as(self.jobseeker)

        response = self.client.get(reverse("chat-api", args=[self.application.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["content"], "Hello")

    def test_authenticated_post_creates_message(self):
        self.login_as(self.jobseeker)

        response = self.client.post(
            reverse("chat-api", args=[self.application.pk]),
            {
                "application": self.application.pk,
                "content": "New message",
                "created_by": self.jobseeker_profile.pk,
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            ConversationMessages.objects.filter(content="New message").exists()
        )

    def test_invalid_post_is_rejected(self):
        self.login_as(self.jobseeker)

        response = self.client.post(
            reverse("chat-api", args=[self.application.pk]),
            {"application": self.application.pk},
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(ConversationMessages.objects.filter(content="").exists())


class ApiConversionViewSetTests(MainTestCase):
    def setUp(self):
        self.employer, self.employer_profile = self.make_account_with_profile(
            role="employer"
        )
        self.jobseeker, self.jobseeker_profile = self.make_account_with_profile(
            role="jobseeker"
        )
        self.job = self.make_job(self.employer_profile)
        self.application = self.make_application(self.job, self.jobseeker_profile)
        self.message = ConversationMessages.objects.create(
            application=self.application,
            content="Existing message",
            created_by=self.jobseeker_profile,
        )

    def test_list_returns_existing_messages(self):
        response = self.client.get("/api/v1/conversion/")

        self.assertEqual(response.status_code, 200)
        contents = [item["content"] for item in response.data]
        self.assertIn("Existing message", contents)

    def test_create_persists_message(self):
        response = self.client.post(
            "/api/v1/conversion/",
            {
                "application": self.application.pk,
                "content": "Created via viewset",
                "created_by": self.jobseeker_profile.pk,
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            ConversationMessages.objects.filter(content="Created via viewset").exists()
        )

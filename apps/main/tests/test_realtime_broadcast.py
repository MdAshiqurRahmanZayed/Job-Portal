from datetime import date, timedelta

from asgiref.sync import sync_to_async
from channels.testing import WebsocketCommunicator
from django.test import TransactionTestCase

from apps.accounts.models import Account, UserProfile
from apps.main import services
from apps.main.consumers import RealtimeConsumer
from apps.main.forms import ConversationMessagesForm, applicationForm
from apps.main.models import Application, Category, Job

from .base import TEST_FIXTURE_PASSWORD, make_test_file, make_test_image


def _make_account_with_profile(role, email):
    account = Account.objects.create_user(
        email=email, username=email.split("@")[0], password=TEST_FIXTURE_PASSWORD
    )
    account.is_active = True
    account.save()
    profile = UserProfile.objects.create(
        user=account,
        first_name="Test",
        last_name="User",
        father_name="Father",
        mother_name="Mother",
        religion="None",
        nationality="Bangladeshi",
        occupation="Engineer",
        nid_no=123456789,
        nid_image=make_test_image(),
        birth_date=date(1995, 1, 1),
        linkedin="https://linkedin.com/in/test",
        about="About me",
        present_address="Present address",
        permanent_address="Permanent address",
        gender="M",
        marital_status="Unmarried",
        role=role,
    )
    return account, profile


class BroadcastDeliveryTests(TransactionTestCase):
    """Confirms create_notification/post_conversation_message actually
    deliver to a connected consumer, not just that the consumer itself
    behaves correctly in isolation (that's test_consumers.py)."""

    def setUp(self):
        self.employer, self.employer_profile = _make_account_with_profile(
            "employer", "bcast-employer@example.com"
        )
        self.jobseeker, self.jobseeker_profile = _make_account_with_profile(
            "jobseeker", "bcast-jobseeker@example.com"
        )
        category = Category.objects.create(name="Engineering", slug="engineering-bc")
        self.job = Job.objects.create(
            user=self.employer_profile,
            title="Software Engineer",
            category=category,
            description="Job description",
            company_name="Acme Inc",
            company_email="hr@acme.example.com",
            job_type="fulltime",
            website_url="https://acme.example.com",
            deadline=date.today() + timedelta(days=30),
            is_published=True,
        )

    async def test_submit_application_delivers_notification_to_employer(self):
        communicator = WebsocketCommunicator(RealtimeConsumer.as_asgi(), "/ws/updates/")
        communicator.scope["user"] = self.employer
        communicator.scope["url_route"] = {"kwargs": {}}
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        form = applicationForm(
            {"content": "I would like to apply"}, {"resume": make_test_file()}
        )
        form.is_valid()
        await sync_to_async(services.submit_application)(
            self.jobseeker_profile, self.job, form
        )

        event = await communicator.receive_from(timeout=2)
        self.assertIn("application", event)

        await communicator.disconnect()

    async def test_chat_message_delivers_to_other_participant(self):
        application = await sync_to_async(Application.objects.create)(
            job=self.job,
            user=self.jobseeker_profile,
            content="Application content",
            resume=make_test_file(),
        )

        communicator = WebsocketCommunicator(
            RealtimeConsumer.as_asgi(), f"/ws/updates/{application.id}/"
        )
        communicator.scope["user"] = self.employer
        communicator.scope["url_route"] = {"kwargs": {"application_id": application.id}}
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        form = ConversationMessagesForm({"content": "hello"})
        form.is_valid()
        await sync_to_async(services.post_conversation_message)(
            self.jobseeker_profile, application, form
        )

        event = await communicator.receive_from(timeout=2)
        self.assertIn("hello", event)

        await communicator.disconnect()

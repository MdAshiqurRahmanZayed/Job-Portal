from datetime import date, timedelta

from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import AnonymousUser
from django.test import TransactionTestCase

from apps.accounts.models import Account, UserProfile
from apps.main.consumers import RealtimeConsumer
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


def _make_job(employer_profile):
    category = Category.objects.create(name="Engineering", slug="engineering-ws")
    return Job.objects.create(
        user=employer_profile,
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


def _communicator_for(account, path, application_id=None):
    communicator = WebsocketCommunicator(RealtimeConsumer.as_asgi(), path)
    communicator.scope["user"] = account
    kwargs = {}
    if application_id is not None:
        kwargs["application_id"] = application_id
    communicator.scope["url_route"] = {"kwargs": kwargs}
    return communicator


class NotificationOnlyConnectionTests(TransactionTestCase):
    """The bare /ws/updates/ connection: notifications only, no
    application_id, so no chat group is joined."""

    def setUp(self):
        self.account, self.profile = _make_account_with_profile(
            "jobseeker", "notif-user@example.com"
        )

    async def test_authenticated_connect_succeeds(self):
        communicator = _communicator_for(self.account, "/ws/updates/")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()

    async def test_unauthenticated_connect_is_rejected(self):
        communicator = _communicator_for(AnonymousUser(), "/ws/updates/")
        connected, _ = await communicator.connect()
        self.assertFalse(connected)


class ChatConnectionTests(TransactionTestCase):
    """The /ws/updates/<application_id>/ connection: joins both the
    notifications group and the chat group for that application."""

    def setUp(self):
        self.employer, self.employer_profile = _make_account_with_profile(
            "employer", "chat-employer@example.com"
        )
        self.jobseeker, self.jobseeker_profile = _make_account_with_profile(
            "jobseeker", "chat-jobseeker@example.com"
        )
        self.job = _make_job(self.employer_profile)
        self.application = Application.objects.create(
            job=self.job,
            user=self.jobseeker_profile,
            content="Application content",
            resume=make_test_file(),
        )
        self.unrelated, _ = _make_account_with_profile(
            "jobseeker", "chat-unrelated@example.com"
        )

    def _communicator_for(self, account):
        return _communicator_for(
            account,
            f"/ws/updates/{self.application.id}/",
            application_id=self.application.id,
        )

    async def test_applicant_connect_succeeds(self):
        communicator = self._communicator_for(self.jobseeker)
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()

    async def test_job_owner_connect_succeeds(self):
        communicator = self._communicator_for(self.employer)
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()

    async def test_unrelated_user_connect_is_rejected(self):
        communicator = self._communicator_for(self.unrelated)
        connected, _ = await communicator.connect()
        self.assertFalse(connected)

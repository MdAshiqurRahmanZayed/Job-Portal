"""Real-browser tests for the WebSocket-driven frontend: confirms pushed
payloads update the DOM directly (no HTTP re-fetch) - see
apps/main/services.py's _broadcast() calls and static/js/main.js /
templates/main/view-application-job.html's onmessage handlers.

Uses Playwright (not a JS test framework - this project has none) driven
against a real Daphne+Redis server via channels.testing.ChannelsLiveServerTestCase,
since plain Django LiveServerTestCase is WSGI-only and can't serve
WebSocket upgrades at all.
"""

import os
import threading
import unittest
from datetime import date, timedelta
from urllib.parse import urlparse

from channels.testing import ChannelsLiveServerTestCase
from decouple import config
from playwright.sync_api import sync_playwright

# Playwright's sync API installs an asyncio event loop on the calling thread
# (it drives its own loop via greenlets on that same thread), which trips
# Django's async-unsafe ORM guard even though this test's DB calls are made
# from plain synchronous test code, not from an async context.
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

from apps.accounts.models import Account, UserProfile
from apps.main import services
from apps.main.models import Application, Category, Job

from .base import TEST_FIXTURE_PASSWORD, make_test_file, make_test_image

# ChannelsLiveServerTestCase refuses to run against an in-memory sqlite
# database. Run this module with FILE_TEST_DB=true (see settings/base.py)
# to get a file-based sqlite test DB instead of the project's default
# in-memory one.


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


def _run_in_thread(fn, *args, **kwargs):
    """Runs fn on a plain background thread and waits for it.

    services.py's _broadcast() calls channels' async_to_sync(), which
    refuses to run on a thread that already has a running asyncio event
    loop - and Playwright's sync API keeps exactly such a loop running on
    this test's main thread. A real HTTP request triggering this same
    write would never land on the browser-driving thread either, so this
    also matches how the write path actually runs in production.
    """
    error = []

    def target():
        try:
            fn(*args, **kwargs)
        except Exception as exc:  # noqa: BLE001
            error.append(exc)

    thread = threading.Thread(target=target)
    thread.start()
    thread.join()
    if error:
        raise error[0]


@unittest.skipUnless(
    config("FILE_TEST_DB", default=False, cast=bool),
    "requires FILE_TEST_DB=true (a file-based sqlite test DB - "
    "ChannelsLiveServerTestCase refuses to run against the project's "
    "default in-memory one) and a reachable Redis (REDIS_HOST)",
)
class RealtimeFrontendTests(ChannelsLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        super().tearDownClass()

    def setUp(self):
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

    def tearDown(self):
        self.context.close()

    def _login(self, account):
        self.client.login(email=account.email, password=TEST_FIXTURE_PASSWORD)
        sessionid = self.client.cookies["sessionid"].value
        host = urlparse(self.live_server_url).hostname
        self.context.add_cookies(
            [{"name": "sessionid", "value": sessionid, "domain": host, "path": "/"}]
        )

    def test_notification_push_updates_dom_without_refetch(self):
        watcher_account, watcher_profile = _make_account_with_profile(
            "employer", "pw-watcher@example.com"
        )
        applicant_account, applicant_profile = _make_account_with_profile(
            "jobseeker", "pw-applicant@example.com"
        )
        category = Category.objects.create(name="PW Cat", slug="pw-cat")
        job = Job.objects.create(
            user=watcher_profile,
            title="PW Job",
            category=category,
            description="desc",
            company_name="Acme",
            company_email="a@a.com",
            job_type="fulltime",
            website_url="https://a.com",
            deadline=date.today() + timedelta(days=30),
            is_published=True,
        )

        self._login(watcher_account)

        notification_count_requests = []
        self.page.on(
            "request",
            lambda req: notification_count_requests.append(req.url)
            if "/notifications-count/" in req.url
            else None,
        )

        self.page.goto(f"{self.live_server_url}/accounts/dashboard/")
        self.page.wait_for_selector("#notifications-count")
        self.page.wait_for_timeout(500)  # let the WebSocket connect

        self.assertEqual(
            len(notification_count_requests),
            1,
            "expected exactly one initial fetch before any push",
        )
        before = self.page.locator("#notifications-count").text_content()

        # Real write path (same as an HTTP request would use) - creates the
        # Application and broadcasts a notification.new push to watcher_profile.
        def do_write():
            application = Application.objects.create(
                job=job,
                user=applicant_profile,
                content="hi",
                resume=make_test_file(),
            )
            services.create_notification(
                to_user=watcher_profile,
                notification_type="application",
                created_by=applicant_profile,
                application=application,
                extra_id=application.id,
            )

        _run_in_thread(do_write)

        self.page.wait_for_function(
            f"document.getElementById('notifications-count').textContent !== '{before}'",
            timeout=5000,
        )
        after = self.page.locator("#notifications-count").text_content()
        self.assertEqual(int(after), int(before) + 1)

        # The push must not have triggered a second HTTP fetch.
        self.assertEqual(
            len(notification_count_requests),
            1,
            "push should update the DOM directly, not trigger a re-fetch",
        )

    def test_chat_push_appends_message_without_refetch(self):
        employer_account, employer_profile = _make_account_with_profile(
            "employer", "pw-chat-employer@example.com"
        )
        jobseeker_account, jobseeker_profile = _make_account_with_profile(
            "jobseeker", "pw-chat-jobseeker@example.com"
        )
        category = Category.objects.create(name="PW Chat Cat", slug="pw-chat-cat")
        job = Job.objects.create(
            user=employer_profile,
            title="PW Chat Job",
            category=category,
            description="desc",
            company_name="Acme",
            company_email="a@a.com",
            job_type="fulltime",
            website_url="https://a.com",
            deadline=date.today() + timedelta(days=30),
            is_published=True,
        )
        application = Application.objects.create(
            job=job,
            user=jobseeker_profile,
            content="hi",
            resume=make_test_file(),
        )

        self._login(employer_account)

        chat_api_requests = []
        self.page.on(
            "request",
            lambda req: chat_api_requests.append(req.url)
            if "/api/v1/chat-messages/" in req.url
            else None,
        )

        self.page.goto(f"{self.live_server_url}/view-application/{application.id}/")
        self.page.wait_for_selector("#single-chat")
        self.page.wait_for_timeout(500)  # let the WebSocket connect

        self.assertEqual(
            len(chat_api_requests),
            1,
            "expected exactly one initial fetch before any push",
        )

        from apps.main.forms import ConversationMessagesForm

        def do_write():
            form = ConversationMessagesForm({"content": "Live pushed message"})
            form.is_valid()
            services.post_conversation_message(jobseeker_profile, application, form)

        _run_in_thread(do_write)

        self.page.wait_for_selector(
            "#single-chat >> text=Live pushed message", timeout=5000
        )

        # The push must not have triggered a second HTTP fetch.
        self.assertEqual(
            len(chat_api_requests),
            1,
            "push should append the message directly, not trigger a re-fetch",
        )

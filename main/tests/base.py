from datetime import date, timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from accounts.models import Account, UserProfile
from main.models import Application, Category, Job

TEST_FIXTURE_PASSWORD = "test-fixture-pw-1"  # nosec: not a real credential

SMALL_GIF = (
    b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04"
    b"\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02"
    b"\x02\x4c\x01\x00\x3b"
)


def make_test_image(name="test.gif"):
    return SimpleUploadedFile(name, SMALL_GIF, content_type="image/gif")


def make_test_file(name="resume.txt", content=b"resume content"):
    return SimpleUploadedFile(name, content, content_type="text/plain")


_unique_counter = 0


def _next_unique():
    global _unique_counter
    _unique_counter += 1
    return _unique_counter


class MainTestCase(TestCase):
    def make_account_with_profile(self, role="jobseeker", email=None, **overrides):
        email = email or f"user{_next_unique()}@example.com"
        username = email.split("@")[0]
        account = Account.objects.create_user(
            email=email, username=username, password=TEST_FIXTURE_PASSWORD
        )
        account.is_active = True
        account.save()

        fields = {
            "user": account,
            "first_name": "Test",
            "last_name": "User",
            "father_name": "Father",
            "mother_name": "Mother",
            "religion": "None",
            "nationality": "Bangladeshi",
            "occupation": "Engineer",
            "nid_no": 123456789,
            "nid_image": make_test_image(),
            "birth_date": date(1995, 1, 1),
            "linkedin": "https://linkedin.com/in/test",
            "about": "About me",
            "present_address": "Present address",
            "permanent_address": "Permanent address",
            "gender": "M",
            "marital_status": "Unmarried",
            "role": role,
        }
        fields.update(overrides)
        profile = UserProfile.objects.create(**fields)
        return account, profile

    def make_category(self, name=None, slug=None):
        n = _next_unique()
        name = name or f"Engineering {n}"
        slug = slug or f"engineering-{n}"
        return Category.objects.create(name=name, slug=slug)

    def make_job(self, employer_profile, category=None, **overrides):
        category = category or self.make_category()
        fields = {
            "user": employer_profile,
            "title": "Software Engineer",
            "category": category,
            "description": "Job description",
            "company_name": "Acme Inc",
            "company_email": "hr@acme.example.com",
            "job_type": "fulltime",
            "website_url": "https://acme.example.com",
            "deadline": date.today() + timedelta(days=30),
            "is_published": True,
        }
        fields.update(overrides)
        return Job.objects.create(**fields)

    def make_application(self, job, applicant_profile, **overrides):
        fields = {
            "job": job,
            "user": applicant_profile,
            "content": "Application content",
            "resume": make_test_file(),
        }
        fields.update(overrides)
        return Application.objects.create(**fields)

    def login_as(self, account):
        self.client.force_login(account)

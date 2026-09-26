from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from apps.accounts.models import Account, UserProfile

TEST_FIXTURE_PASSWORD = "test-fixture-pw-1"  # nosec: not a real credential

SMALL_GIF = (
    b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04"
    b"\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02"
    b"\x02\x4c\x01\x00\x3b"
)


def make_test_image(name="test.gif"):
    return SimpleUploadedFile(name, SMALL_GIF, content_type="image/gif")


class AccountsTestCase(TestCase):
    def make_account(
        self, email="user@example.com", password=TEST_FIXTURE_PASSWORD, is_active=True
    ):
        username = email.split("@")[0]
        account = Account.objects.create_user(
            email=email, username=username, password=password
        )
        account.is_active = is_active
        account.save()
        return account

    def make_profile(self, account, role="jobseeker", **overrides):
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
            "nid_image": make_test_image("nid.gif"),
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
        return UserProfile.objects.create(**fields)

    def login_as(self, account, password=TEST_FIXTURE_PASSWORD):
        self.client.force_login(account)

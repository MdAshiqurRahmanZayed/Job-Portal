from django.urls import reverse

from accounts.models import Education, UserProfile, mobileNumber

from .base import AccountsTestCase, make_test_image

OLD_FIXTURE_PASSWORD = "test-fixture-pw-old"  # nosec: not a real credential
NEW_FIXTURE_PASSWORD = "test-fixture-pw-new"  # nosec: not a real credential


class ProfileTests(AccountsTestCase):
    def setUp(self):
        self.account = self.make_account(email="profile@example.com")

    def test_authenticated_profile_create_persists(self):
        self.login_as(self.account)

        response = self.client.post(
            reverse("createUserProfile"),
            {
                "first_name": "Test",
                "last_name": "User",
                "father_name": "Father",
                "mother_name": "Mother",
                "religion": "None",
                "nationality": "Bangladeshi",
                "occupation": "Engineer",
                "nid_no": 123456789,
                "nid_image": make_test_image(),
                "birth_date": "1995-01-01",
                "linkedin": "https://linkedin.com/in/test",
                "about": "About me",
                "present_address": "Present address",
                "permanent_address": "Permanent address",
                "gender": "M",
                "marital_status": "Unmarried",
                "role": "jobseeker",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(UserProfile.objects.filter(user=self.account).exists())

    def test_unauthenticated_profile_create_is_rejected(self):
        response = self.client.post(reverse("createUserProfile"), {})

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)
        self.assertFalse(UserProfile.objects.filter(user=self.account).exists())

    def test_authenticated_profile_update_persists(self):
        self.make_profile(self.account)
        self.login_as(self.account)

        response = self.client.post(
            reverse("updateUserPeofile"),
            {
                "first_name": "Updated",
                "last_name": "User",
                "father_name": "Father",
                "mother_name": "Mother",
                "religion": "None",
                "nationality": "Bangladeshi",
                "occupation": "Engineer",
                "nid_no": 123456789,
                "nid_image": make_test_image(),
                "birth_date": "1995-01-01",
                "linkedin": "https://linkedin.com/in/test",
                "about": "About me",
                "present_address": "Present address",
                "permanent_address": "Permanent address",
                "gender": "M",
                "marital_status": "Unmarried",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            UserProfile.objects.get(user=self.account).first_name, "Updated"
        )


class ShowProfileTests(AccountsTestCase):
    def test_view_profile_returns_expected_data(self):
        account = self.make_account(email="viewme@example.com")
        profile = self.make_profile(account, role="employer")
        self.login_as(account)

        response = self.client.get(reverse("showUserProfile", args=[profile.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["userprofile"], profile)


class EducationTests(AccountsTestCase):
    def setUp(self):
        self.account = self.make_account(email="edu@example.com")
        self.profile = self.make_profile(self.account, role="jobseeker")

    def test_authenticated_education_create_persists(self):
        self.login_as(self.account)

        response = self.client.post(reverse("createEducation"), {})

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Education.objects.filter(user=self.profile).exists())

    def test_unauthenticated_education_create_is_rejected(self):
        response = self.client.post(reverse("createEducation"), {})

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)
        self.assertFalse(Education.objects.filter(user=self.profile).exists())

    def test_authenticated_education_update_persists(self):
        Education.objects.create(user=self.profile, ssc_group="science")
        self.login_as(self.account)

        response = self.client.post(
            reverse("updateEducation"), {"ssc_group": "commerce"}
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Education.objects.get(user=self.profile).ssc_group, "commerce")


class MobileNumberTests(AccountsTestCase):
    def setUp(self):
        self.account = self.make_account(email="mobile@example.com")
        self.profile = self.make_profile(self.account, role="jobseeker")

    def test_authenticated_create_persists(self):
        self.login_as(self.account)

        response = self.client.post(
            reverse("createMobileNumber"), {"mobile_number": "1500000000"}
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(mobileNumber.objects.filter(userprofile=self.profile).exists())

    def test_unauthenticated_create_is_rejected(self):
        response = self.client.post(
            reverse("createMobileNumber"), {"mobile_number": "1500000000"}
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)
        self.assertFalse(mobileNumber.objects.filter(userprofile=self.profile).exists())

    def test_authenticated_update_persists(self):
        mobile = mobileNumber.objects.create(
            userprofile=self.profile, mobile_number=1500000000
        )
        self.login_as(self.account)

        self.client.post(
            reverse("updateMobileNumber", args=[mobile.pk]),
            {"mobile_number": "1600000000"},
        )

        mobile.refresh_from_db()
        self.assertEqual(mobile.mobile_number, 1600000000)

    def test_authenticated_delete_removes_record(self):
        mobile = mobileNumber.objects.create(
            userprofile=self.profile, mobile_number=1500000000
        )
        self.login_as(self.account)

        self.client.post(reverse("deleteMobileNumber", args=[mobile.pk]))

        self.assertFalse(mobileNumber.objects.filter(pk=mobile.pk).exists())

    def test_unauthenticated_delete_is_rejected(self):
        mobile = mobileNumber.objects.create(
            userprofile=self.profile, mobile_number=1500000000
        )

        response = self.client.post(reverse("deleteMobileNumber", args=[mobile.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)
        self.assertTrue(mobileNumber.objects.filter(pk=mobile.pk).exists())


class ChangePasswordTests(AccountsTestCase):
    def setUp(self):
        self.account = self.make_account(
            email="pwd@example.com", password=OLD_FIXTURE_PASSWORD
        )

    def test_authenticated_user_can_change_password(self):
        self.login_as(self.account)

        response = self.client.post(
            reverse("change_password"),
            {
                "current_password": OLD_FIXTURE_PASSWORD,
                "new_password": NEW_FIXTURE_PASSWORD,
                "confirm_password": NEW_FIXTURE_PASSWORD,
            },
        )

        self.assertEqual(response.status_code, 302)

        self.client.logout()
        login_response = self.client.post(
            reverse("login"),
            {"email": "pwd@example.com", "password": NEW_FIXTURE_PASSWORD},
        )
        self.assertIn("_auth_user_id", self.client.session)
        self.assertEqual(login_response.status_code, 302)

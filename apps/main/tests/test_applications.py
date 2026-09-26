from django.urls import reverse

from apps.main.models import Application

from .base import MainTestCase, make_test_file


class ApplicationSubmissionTests(MainTestCase):
    def setUp(self):
        self.employer, self.employer_profile = self.make_account_with_profile(
            role="employer"
        )
        self.jobseeker, self.jobseeker_profile = self.make_account_with_profile(
            role="jobseeker"
        )
        self.job = self.make_job(self.employer_profile)

    def test_authenticated_jobseeker_can_submit_application(self):
        self.login_as(self.jobseeker)

        response = self.client.post(
            reverse("createApplication", args=[self.job.pk]),
            {"content": "I would like to apply", "resume": make_test_file()},
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Application.objects.filter(
                job=self.job, user=self.jobseeker_profile
            ).exists()
        )

    def test_employer_cannot_submit_application(self):
        self.login_as(self.employer)

        self.client.post(
            reverse("createApplication", args=[self.job.pk]),
            {"content": "I would like to apply", "resume": make_test_file()},
        )

        self.assertFalse(Application.objects.filter(job=self.job).exists())


class ApplicationListingTests(MainTestCase):
    def setUp(self):
        self.employer, self.employer_profile = self.make_account_with_profile(
            role="employer"
        )
        self.jobseeker, self.jobseeker_profile = self.make_account_with_profile(
            role="jobseeker"
        )
        self.other_jobseeker, self.other_profile = self.make_account_with_profile(
            role="jobseeker"
        )
        self.job = self.make_job(self.employer_profile)
        self.application = self.make_application(self.job, self.jobseeker_profile)

    def test_applicant_sees_only_own_applications(self):
        other_job = self.make_job(self.employer_profile, title="Other Job")
        self.make_application(other_job, self.other_profile)

        self.login_as(self.jobseeker)
        response = self.client.get(reverse("allApplication"))

        applications = list(response.context["applications"])
        self.assertEqual(applications, [self.application])

    def test_job_owner_can_view_applicants(self):
        self.login_as(self.employer)

        response = self.client.get(reverse("allApplicant", args=[self.job.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["job"], self.job)

    def test_non_owner_cannot_view_applicants(self):
        other_employer, _ = self.make_account_with_profile(role="employer")
        self.login_as(other_employer)

        response = self.client.get(reverse("allApplicant", args=[self.job.pk]))

        self.assertEqual(response.status_code, 404)


class ApplicationViewDeleteTests(MainTestCase):
    def setUp(self):
        self.employer, self.employer_profile = self.make_account_with_profile(
            role="employer"
        )
        self.jobseeker, self.jobseeker_profile = self.make_account_with_profile(
            role="jobseeker"
        )
        self.job = self.make_job(self.employer_profile)
        self.application = self.make_application(self.job, self.jobseeker_profile)

    def test_applicant_can_view_own_application(self):
        self.login_as(self.jobseeker)

        response = self.client.get(
            reverse("viewApplication", args=[self.application.pk])
        )

        self.assertEqual(response.status_code, 200)

    def test_job_owner_can_view_application(self):
        self.login_as(self.employer)

        response = self.client.get(
            reverse("viewApplication", args=[self.application.pk])
        )

        self.assertEqual(response.status_code, 200)

    def test_unrelated_user_cannot_view_application(self):
        unrelated, _ = self.make_account_with_profile(role="jobseeker")
        self.login_as(unrelated)

        response = self.client.get(
            reverse("viewApplication", args=[self.application.pk])
        )

        self.assertEqual(response.status_code, 404)

    def test_applicant_can_delete_own_application(self):
        self.login_as(self.jobseeker)

        self.client.post(reverse("deleteApplication", args=[self.application.pk]))

        self.assertFalse(Application.objects.filter(pk=self.application.pk).exists())

    def test_unrelated_user_cannot_delete_application(self):
        unrelated, _ = self.make_account_with_profile(role="jobseeker")
        self.login_as(unrelated)

        response = self.client.post(
            reverse("deleteApplication", args=[self.application.pk])
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Application.objects.filter(pk=self.application.pk).exists())

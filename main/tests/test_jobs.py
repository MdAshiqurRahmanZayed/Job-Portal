from django.urls import reverse

from main.models import Job

from .base import MainTestCase


class JobCreateTests(MainTestCase):
    def setUp(self):
        self.category = self.make_category()
        self.employer, self.employer_profile = self.make_account_with_profile(
            role="employer"
        )

    def _valid_job_payload(self):
        return {
            "title": "Backend Developer",
            "category": self.category.id,
            "description": "We need a backend developer.",
            "company_name": "Acme Inc",
            "company_email": "hr@acme.example.com",
            "vacancy": 1,
            "location": "Remote",
            "job_type": "fulltime",
            "website_url": "https://acme.example.com",
            "deadline": "2099-12-31",
            "is_published": True,
            "is_closed": False,
        }

    def test_authenticated_employer_can_create_job(self):
        self.login_as(self.employer)

        response = self.client.post(reverse("createJob"), self._valid_job_payload())

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Job.objects.filter(title="Backend Developer").exists())

    def test_unauthenticated_create_is_rejected(self):
        response = self.client.post(reverse("createJob"), self._valid_job_payload())

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)
        self.assertFalse(Job.objects.filter(title="Backend Developer").exists())

    def test_jobseeker_cannot_create_job(self):
        jobseeker, _ = self.make_account_with_profile(role="jobseeker")
        self.login_as(jobseeker)

        self.client.post(reverse("createJob"), self._valid_job_payload())

        self.assertFalse(Job.objects.filter(title="Backend Developer").exists())


class JobUpdateDeleteTests(MainTestCase):
    def setUp(self):
        self.owner, self.owner_profile = self.make_account_with_profile(role="employer")
        self.other, self.other_profile = self.make_account_with_profile(role="employer")
        self.job = self.make_job(self.owner_profile)

    def test_owner_can_update_job(self):
        self.login_as(self.owner)

        response = self.client.post(
            reverse("updateJob", args=[self.job.pk]),
            {
                "title": "Updated Title",
                "category": self.job.category.id,
                "description": self.job.description,
                "company_name": self.job.company_name,
                "company_email": self.job.company_email,
                "location": self.job.location,
                "job_type": self.job.job_type,
                "website_url": self.job.website_url,
                "deadline": self.job.deadline,
                "is_published": True,
                "is_closed": False,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.job.refresh_from_db()
        self.assertEqual(self.job.title, "Updated Title")

    def test_non_owner_cannot_update_job(self):
        self.login_as(self.other)

        self.client.post(
            reverse("updateJob", args=[self.job.pk]),
            {
                "title": "Hijacked Title",
                "category": self.job.category.id,
                "description": self.job.description,
                "company_name": self.job.company_name,
                "company_email": self.job.company_email,
                "location": self.job.location,
                "job_type": self.job.job_type,
                "website_url": self.job.website_url,
                "deadline": self.job.deadline,
                "is_published": True,
                "is_closed": False,
            },
        )

        self.job.refresh_from_db()
        self.assertNotEqual(self.job.title, "Hijacked Title")

    def test_owner_can_delete_job(self):
        self.login_as(self.owner)

        self.client.post(reverse("deleteJob", args=[self.job.pk]))

        self.assertFalse(Job.objects.filter(pk=self.job.pk).exists())

    def test_non_owner_cannot_delete_job(self):
        self.login_as(self.other)

        self.client.post(reverse("deleteJob", args=[self.job.pk]))

        self.assertTrue(Job.objects.filter(pk=self.job.pk).exists())


class JobListingDetailTests(MainTestCase):
    def setUp(self):
        self.employer, self.employer_profile = self.make_account_with_profile(
            role="employer"
        )
        self.jobseeker, _ = self.make_account_with_profile(role="jobseeker")
        self.category = self.make_category()
        self.job = self.make_job(self.employer_profile, category=self.category)

    def test_listing_returns_existing_jobs(self):
        response = self.client.get(reverse("allJobs"))

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.job, response.context["jobs"])

    def test_detail_view_returns_job_data(self):
        self.login_as(self.jobseeker)

        response = self.client.get(
            reverse("jobDetail", args=[self.job.slug, self.job.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["job"], self.job)

    def test_category_filter_returns_only_matching_jobs(self):
        other_category = self.make_category(name="Design", slug="design")
        other_job = self.make_job(
            self.employer_profile, category=other_category, title="Designer"
        )

        response = self.client.get(reverse("categoriesJobs", args=[self.category.slug]))

        jobs_in_page = list(response.context["jobs"])
        self.assertIn(self.job, jobs_in_page)
        self.assertNotIn(other_job, jobs_in_page)

    def test_search_returns_matching_jobs(self):
        response = self.client.get(reverse("searchJobs"), {"keyword": "Software"})

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.job, response.context["jobs"])

    def test_my_created_jobs_returns_only_own_jobs(self):
        other_employer, other_profile = self.make_account_with_profile(role="employer")
        other_job = self.make_job(
            other_profile, category=self.category, title="Other Employer Job"
        )
        self.login_as(self.employer)

        response = self.client.get(reverse("myCreatedJobs"))

        jobs_in_page = list(response.context["jobs"])
        self.assertIn(self.job, jobs_in_page)
        self.assertNotIn(other_job, jobs_in_page)

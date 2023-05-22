# Generated by Django 4.1.3 on 2023-05-02 13:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0005_remove_userprofile_education"),
    ]

    operations = [
        migrations.CreateModel(
            name="Education",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "ssc_group",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("science", "Science"),
                            ("commerce", "Commerce"),
                            ("arts", "Arts"),
                        ],
                        max_length=10,
                        null=True,
                    ),
                ),
                ("ssc_year", models.DateField(blank=True, null=True)),
                (
                    "ssc_board",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("dhaka", "Dhaka"),
                            ("rajshahi", "Rajshahi"),
                            ("comilla", "Comilla"),
                            ("jessore", "Jessore"),
                            ("chittagong", "Chittagong"),
                            ("barisal", "Barisal"),
                            ("sylhet", "Sylhet"),
                            ("dinajpur", "Dinajpur"),
                            ("madrasah", "Madrasah"),
                            ("technical", "Technical"),
                        ],
                        max_length=50,
                        null=True,
                    ),
                ),
                (
                    "ssc_institution",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                ("ssc_cgpa", models.FloatField(blank=True, null=True)),
                (
                    "ssc_certificate",
                    models.FileField(
                        blank=True, null=True, upload_to="applicant/certificate/"
                    ),
                ),
                (
                    "hsc_group",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("science", "Science"),
                            ("commerce", "Commerce"),
                            ("arts", "Arts"),
                        ],
                        max_length=10,
                        null=True,
                    ),
                ),
                ("hsc_year", models.DateField(blank=True, null=True)),
                (
                    "hsc_board",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("dhaka", "Dhaka"),
                            ("rajshahi", "Rajshahi"),
                            ("comilla", "Comilla"),
                            ("jessore", "Jessore"),
                            ("chittagong", "Chittagong"),
                            ("barisal", "Barisal"),
                            ("sylhet", "Sylhet"),
                            ("dinajpur", "Dinajpur"),
                            ("madrasah", "Madrasah"),
                            ("technical", "Technical"),
                        ],
                        max_length=50,
                        null=True,
                    ),
                ),
                ("hsc_cgpa", models.FloatField(blank=True, null=True)),
                (
                    "hsc_institution",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                (
                    "hsc_certificate",
                    models.FileField(
                        blank=True, null=True, upload_to="applicant/certificate/"
                    ),
                ),
                ("bsc_session", models.CharField(blank=True, max_length=20, null=True)),
                (
                    "bsc_institution",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                ("bsc_graduation_year", models.DateField(blank=True, null=True)),
                ("bsc_subject", models.CharField(blank=True, max_length=50, null=True)),
                ("bsc_cgpa", models.FloatField(blank=True, null=True)),
                (
                    "bsc_certificate",
                    models.FileField(
                        blank=True, null=True, upload_to="applicant/certificate/"
                    ),
                ),
                ("msc_session", models.CharField(blank=True, max_length=20, null=True)),
                (
                    "msc_institution",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                ("msc_graduation_year", models.DateField(blank=True, null=True)),
                ("msc_subject", models.CharField(blank=True, max_length=50, null=True)),
                ("msc_cgpa", models.FloatField(blank=True, null=True)),
                (
                    "msc_certificate",
                    models.FileField(
                        blank=True, null=True, upload_to="applicant/certificate/"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="UserEducation",
                        to="accounts.userprofile",
                    ),
                ),
            ],
        ),
    ]

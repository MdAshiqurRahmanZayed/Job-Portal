# Generated by Django 4.1.3 on 2023-05-05 03:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0006_education"),
        ("main", "0011_alter_application_job_conversationmessages"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="conversationmessages",
            options={"ordering": ["created_at"]},
        ),
        migrations.AlterField(
            model_name="job",
            name="job_type",
            field=models.CharField(
                choices=[
                    ("fulltime", "Full time"),
                    ("parttime", "Part time"),
                    ("remote", "Remote"),
                    ("internship", "Internship"),
                ],
                max_length=10,
            ),
        ),
        migrations.CreateModel(
            name="Notification",
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
                    "notification_type",
                    models.CharField(
                        choices=[
                            ("message", "message"),
                            ("application", "application"),
                        ],
                        max_length=20,
                    ),
                ),
                ("is_seen", models.BooleanField(default=False)),
                ("extra_id", models.IntegerField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="creatednotifications",
                        to="accounts.userprofile",
                    ),
                ),
                (
                    "to_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to="accounts.userprofile",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]

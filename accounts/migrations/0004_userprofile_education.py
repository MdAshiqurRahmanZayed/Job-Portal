# Generated by Django 4.1.3 on 2023-05-02 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_remove_userprofile_education"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="education",
            field=models.BooleanField(default=False),
        ),
    ]

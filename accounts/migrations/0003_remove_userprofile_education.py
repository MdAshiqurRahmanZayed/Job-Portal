# Generated by Django 4.1.3 on 2023-05-02 08:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_userprofile_education"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userprofile",
            name="education",
        ),
    ]

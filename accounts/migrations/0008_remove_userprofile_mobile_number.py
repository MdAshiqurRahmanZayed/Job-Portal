# Generated by Django 4.1.3 on 2023-06-25 04:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0007_userprofile_mobile_number"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userprofile",
            name="mobile_number",
        ),
    ]

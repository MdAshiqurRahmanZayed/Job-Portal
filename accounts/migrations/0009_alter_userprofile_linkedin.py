# Generated by Django 4.1.3 on 2023-06-25 06:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0008_remove_userprofile_mobile_number"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userprofile",
            name="linkedin",
            field=models.CharField(default="https://www.youtube.com/", max_length=50),
            preserve_default=False,
        ),
    ]
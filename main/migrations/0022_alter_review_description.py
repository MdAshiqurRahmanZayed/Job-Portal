# Generated by Django 4.1.3 on 2023-06-27 05:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0021_remove_job_image_job_company_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="review",
            name="description",
            field=models.CharField(max_length=400),
        ),
    ]

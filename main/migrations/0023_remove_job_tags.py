# Generated by Django 4.1.3 on 2023-07-05 13:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0022_alter_review_description"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="job",
            name="tags",
        ),
    ]